#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

import asyncio

from collections import OrderedDict
from dataclasses import dataclass

from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from collections.abc import Iterable


class Cache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be greater than 0")

        self.capacity = capacity
        # An `OrderedDict` rather than a `dict`: the eviction below needs `move_to_end`,
        #  which `dict` has no equivalent of, and `popitem(last=False)` to drop the oldest
        #  entry, where `dict.popitem()` drops the newest.
        self._cache: OrderedDict[Any, Any] = OrderedDict()
        self._lock = asyncio.Lock()

    # Rebuilds the lock and keeps what is cached. Why it has to be rebuilt at all is on
    #  `Client._rebuild_loop_bound_state`.
    def reset_lock(self) -> None:
        self._lock = asyncio.Lock()

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: Any) -> bool:
        return key in self._cache

    def __bool__(self) -> bool:
        return bool(self._cache)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(capacity={self.capacity}, size={len(self)})"

    async def get(self, key: Any, default: Any = None) -> Any:
        async with self._lock:
            if key not in self._cache:
                return default

            self._cache.move_to_end(key)
            return self._cache[key]

    async def set(self, key: Any, value: Any) -> None:
        async with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)

            if len(self._cache) > self.capacity:
                self._cache.popitem(last=False)


@dataclass(frozen=True)
class Sighting:
    """A message a `min` peer was seen in."""

    chat_id: int
    message_id: int


class MinPeerCache:
    """Cache message contexts for `min` peers.

    Maps each marked `min` peer ID to `{chat_id: message_id}`, with
    both levels ordered by the time the sighting was recorded.

    A `min` user or channel may not have an `access_hash` that can be
    used to address it directly. When needed, the client can use an
    `input*FromMessage` constructor with a message in which the peer
    was seen:
    https://core.telegram.org/api/min

    A peer keeps `chats_per_peer` chat contexts rather than one, so
    failure of a single context does not immediately lose the peer;
    the newest sighting is tried first.

    Every ID is marked as returned by `utils.get_peer_id`, so users
    and channels share the map without colliding. Ordering is based
    on when sightings are recorded, not on `message_id`: an older
    message processed later is still the newest sighting.
    """

    def __init__(self, capacity: int, chats_per_peer: int = 3) -> None:
        if capacity <= 0:
            msg = "capacity must be greater than 0"
            raise ValueError(msg)

        if chats_per_peer <= 0:
            msg = "chats_per_peer must be greater than 0"
            raise ValueError(msg)

        self.capacity = capacity
        self.chats_per_peer = chats_per_peer
        # `OrderedDict` at both levels for the reason `Cache` gives: recording a sighting needs
        #  `move_to_end`, and eviction `popitem(last=False)` to drop the least recent entry.
        self._peers: OrderedDict[int, OrderedDict[int, int]] = OrderedDict()
        self._lock = asyncio.Lock()

    # Rebuilds the lock and keeps what is cached. Why it has to be rebuilt at all is on
    #  `Client._rebuild_loop_bound_state`.
    def reset_lock(self) -> None:
        self._lock = asyncio.Lock()

    def __len__(self) -> int:
        return len(self._peers)

    def __contains__(self, peer_id: int) -> bool:
        return peer_id in self._peers

    def __repr__(self) -> str:
        return f"{type(self).__name__}(capacity={self.capacity}, size={len(self)})"

    async def add(self, peer_ids: Iterable[int], chat_id: int, message_id: int) -> None:
        """Record that each of `peer_ids` was seen in `message_id` of `chat_id`."""
        async with self._lock:
            for peer_id in peer_ids:
                if peer_id not in self._peers:
                    self._peers[peer_id] = OrderedDict()

                self._peers.move_to_end(peer_id)

                chats = self._peers[peer_id]
                chats[chat_id] = message_id
                chats.move_to_end(chat_id)

                if len(chats) > self.chats_per_peer:
                    chats.popitem(last=False)

                if len(self._peers) > self.capacity:
                    self._peers.popitem(last=False)

    async def get(self, peer_id: int, chat_id: int | None = None) -> list[Sighting]:
        """Get the sightings of `peer_id`, newest first, or only the one in `chat_id` if given."""
        # A copy, since the caller awaits requests between sightings while new ones land.
        async with self._lock:
            chats = self._peers.get(peer_id)

            if chats is None:
                return []

            if chat_id is not None:
                message_id = chats.get(chat_id)

                return [] if message_id is None else [Sighting(chat_id, message_id)]

            return [Sighting(*item) for item in reversed(chats.items())]

    @overload
    async def discard(self, peer_id: int) -> None: ...

    @overload
    async def discard(self, peer_id: int, chat_id: int) -> None: ...

    @overload
    async def discard(self, peer_id: int, chat_id: int, message_id: int) -> None: ...

    async def discard(
        self,
        peer_id: int,
        chat_id: int | None = None,
        message_id: int | None = None,
    ) -> None:
        """Forget what is known about one peer.

        Only `peer_id`: everything about the peer.
        With `chat_id`: only the sighting in that chat.
        With `message_id` as well: only if the sighting is still that message, so a newer one
        that replaced it in the meantime stays.
        """
        if chat_id is None and message_id is not None:
            msg = "message_id needs a chat_id, message ids are only unique inside a chat"
            raise ValueError(msg)

        async with self._lock:
            chats = self._peers.get(peer_id)

            if chats is None:
                return

            if chat_id is not None:
                if message_id is not None and chats.get(chat_id) != message_id:
                    return

                chats.pop(chat_id, None)

            if chat_id is None or not chats:
                del self._peers[peer_id]

    @overload
    async def discard_messages(self, chat_id: int) -> None: ...

    @overload
    async def discard_messages(self, chat_id: int, message_ids: int | Iterable[int]) -> None: ...

    async def discard_messages(
        self,
        chat_id: int,
        message_ids: int | Iterable[int] | None = None,
    ) -> None:
        """Forget the sightings in a chat, of every peer.

        Only `chat_id`: all of them, e.g. the chat is no longer reachable.
        With `message_ids` as well: only those made in one of these messages, e.g. they were
        deleted. An empty collection forgets nothing.
        """
        # Built before the scan, which is then one pass however many messages are given.
        ids = (
            None
            if message_ids is None
            else {message_ids}
            if isinstance(message_ids, int)
            else set(message_ids)
        )

        if ids is not None and not ids:
            return

        # Scans every peer, so it is meant for the rare event it answers, not for each message.
        async with self._lock:
            emptied = []

            for peer_id, chats in self._peers.items():
                if chat_id not in chats or (ids is not None and chats[chat_id] not in ids):
                    continue

                del chats[chat_id]

                if not chats:
                    emptied.append(peer_id)

            # Deleted afterwards, a dict cannot change size while it is being iterated.
            for peer_id in emptied:
                del self._peers[peer_id]

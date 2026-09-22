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
from typing import Final, overload
from collections.abc import Iterable

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils

# `inputPeerSelf` carries no identifier, so the account's own chat cannot be keyed the way every
#  other one is. The answer names it instead, through the `self` flag on `user`. `0` is free as a
#  key: `get_peer_id()` gives a user id back positive, a chat id negative and a channel id far
#  below that, so no real peer ever lands on it.
_SELF: Final[int] = 0


async def _fetch_channels(
    client: pyrogram.Client,
    *,
    peers: list[raw.types.InputPeerChannel],
) -> list[raw.base.Chat]:
    if not peers:
        return []

    return (await client.invoke(raw.functions.channels.GetChannels(id=peers))).chats


async def _fetch_users(
    client: pyrogram.Client,
    *,
    peers: list[raw.types.InputPeerUser | raw.types.InputPeerSelf],
) -> list[raw.base.User]:
    if not peers:
        return []

    return await client.invoke(raw.functions.users.GetUsers(id=peers))


async def _fetch_basic_chats(
    client: pyrogram.Client,
    *,
    chat_ids: list[int],
) -> list[raw.base.Chat]:
    if not chat_ids:
        return []

    return (await client.invoke(raw.functions.messages.GetChats(id=chat_ids))).chats


async def _fetch_raw_chats(
    client: pyrogram.Client,
    *,
    peers: list[raw.base.InputPeer],
) -> list[raw.base.Chat | raw.base.User]:
    """Ask for every peer, one call per kind of peer, the three concurrently."""

    answers = await asyncio.gather(
        _fetch_channels(
            client,
            peers=[peer for peer in peers if isinstance(peer, raw.types.InputPeerChannel)],
        ),
        _fetch_users(
            client,
            peers=[
                peer
                for peer in peers
                if isinstance(peer, (raw.types.InputPeerUser, raw.types.InputPeerSelf))
            ],
        ),
        _fetch_basic_chats(
            client,
            chat_ids=[peer.chat_id for peer in peers if isinstance(peer, raw.types.InputPeerChat)],
        ),
    )

    return [raw_chat for answer in answers for raw_chat in answer]


async def _parse_by_id(
    client: pyrogram.Client,
    *,
    raw_chats: list[raw.base.Chat | raw.base.User],
) -> dict[int, types.Chat]:
    by_id: dict[int, types.Chat] = {}

    for raw_chat in raw_chats:
        chat = await types.Chat._parse_chat(client, raw_chat)

        # `_parse_chat()` gives `None` back for a `chatEmpty` or a `userEmpty`, which is what an
        #  identifier this account can no longer see comes back as. Leaving it out is what makes
        #  the list below lose that identifier rather than carry a hole nobody can iterate past.
        if chat is None:
            continue

        by_id[_SELF if getattr(raw_chat, "is_self", False) else chat.id] = chat

    return by_id


def _key(peer: raw.base.InputPeer) -> int:
    return _SELF if isinstance(peer, raw.types.InputPeerSelf) else utils.get_peer_id(peer)


def _in_order(
    peers: list[raw.base.InputPeer],
    *,
    by_id: dict[int, types.Chat],
) -> types.List:
    """Every chat the server answered for, in the order the caller asked for them."""

    chats = types.List()

    for peer in peers:
        chat = by_id.get(_key(peer))

        if chat is not None:
            chats.append(chat)

    return chats


class GetChats:
    # `str` is itself an iterable of `str`, so a username matches both overloads.
    #  The single-chat one comes first, resolving it the way the body does.
    @overload
    async def get_chats(  # type: ignore[overload-overlap]
        self: pyrogram.Client,
        chat_ids: int | str,
    ) -> types.Chat | None: ...

    @overload
    async def get_chats(
        self: pyrogram.Client,
        chat_ids: Iterable[int | str],
    ) -> list[types.Chat]: ...

    async def get_chats(
        self: pyrogram.Client,
        chat_ids: int | str | Iterable[int | str],
    ) -> types.Chat | list[types.Chat] | None:
        """Get basic information about one or more chats.

        This is the batching form of :meth:`~pyrogram.Client.get_chat`, and it answers what that
        method answers with ``force_full=False``: one call per kind of peer rather than one call
        per identifier. Full information is a single-chat request on Telegram's side, so ask
        :meth:`~pyrogram.Client.get_chat` for it.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_ids (``int`` | ``str`` | Iterable of ``int`` or ``str``):
                A list of chat identifiers (id or username) or a single chat id/username.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

        Returns:
            :obj:`~pyrogram.types.Chat` | List of :obj:`~pyrogram.types.Chat` | ``None``: In case
            *chat_ids* was not a list, a single chat is returned, otherwise a list of chats is
            returned, in the order asked for. Telegram answers with an empty peer for an identifier
            this account can no longer see, in which case ``None`` is returned for a single
            identifier and the list simply leaves that identifier out. Use
            :meth:`~pyrogram.Client.get_chat` to be told which one is missing.

        Example:
            .. code-block:: python

                # Get information about one chat
                await app.get_chats("me")

                # Get information about multiple chats at once
                await app.get_chats([chat_id1, chat_id2, chat_id3])
        """

        is_iterable: bool = not isinstance(chat_ids, (int, str))
        identifiers = list(chat_ids) if is_iterable else [chat_ids]
        peers = await asyncio.gather(*[self.resolve_peer(identifier) for identifier in identifiers])

        raw_chats = await _fetch_raw_chats(self, peers=peers)
        chats = _in_order(peers, by_id=await _parse_by_id(self, raw_chats=raw_chats))

        return chats if is_iterable else chats[0] if chats else None

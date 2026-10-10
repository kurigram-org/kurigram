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

from typing import Final

import pytest

from pyrogram.utils import MinPeerCache
from pyrogram.utils.cache import Sighting

_USER: Final[int] = 42
_OTHER_USER: Final[int] = 43
_GROUP: Final[int] = -1001
_OTHER_GROUP: Final[int] = -1002
_THIRD_GROUP: Final[int] = -1003


@pytest.mark.parametrize(
    ("capacity", "chats_per_peer", "message"),
    [
        (0, 3, "capacity"),
        (-1, 3, "capacity"),
        (10, 0, "chats_per_peer"),
        (10, -1, "chats_per_peer"),
    ],
)
def test_a_size_below_one_is_rejected(capacity: int, chats_per_peer: int, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        MinPeerCache(capacity, chats_per_peer)


def test_three_chats_are_kept_per_peer_by_default() -> None:
    assert MinPeerCache(10).chats_per_peer == 3


async def test_an_unknown_peer_has_no_sightings() -> None:
    cache = MinPeerCache(10)

    assert await cache.get(_USER) == []
    assert await cache.get(_USER, _GROUP) == []
    assert _USER not in cache
    assert len(cache) == 0


async def test_sightings_come_back_newest_first() -> None:
    cache = MinPeerCache(10)

    await cache.add([_USER], _GROUP, 5)
    await cache.add([_USER], _OTHER_GROUP, 6)

    assert await cache.get(_USER) == [Sighting(_OTHER_GROUP, 6), Sighting(_GROUP, 5)]


async def test_the_last_recorded_sighting_wins_even_for_an_older_message() -> None:
    # Fetching history parses older messages after newer ones. The sighting recorded last is
    #  the one tried first, whatever its message id.
    cache = MinPeerCache(10)

    await cache.add([_USER], _GROUP, 100)
    await cache.add([_USER], _OTHER_GROUP, 1)

    assert (await cache.get(_USER))[0] == Sighting(_OTHER_GROUP, 1)


async def test_a_chat_keeps_one_sighting_which_a_new_one_replaces_and_moves_first() -> None:
    cache = MinPeerCache(10)

    await cache.add([_USER], _GROUP, 5)
    await cache.add([_USER], _OTHER_GROUP, 6)
    await cache.add([_USER], _GROUP, 7)

    assert await cache.get(_USER) == [Sighting(_GROUP, 7), Sighting(_OTHER_GROUP, 6)]


async def test_the_oldest_chat_of_a_peer_goes_past_chats_per_peer() -> None:
    cache = MinPeerCache(10, chats_per_peer=2)

    await cache.add([_USER], _GROUP, 1)
    await cache.add([_USER], _OTHER_GROUP, 2)
    await cache.add([_USER], _THIRD_GROUP, 3)

    assert await cache.get(_USER) == [Sighting(_THIRD_GROUP, 3), Sighting(_OTHER_GROUP, 2)]


async def test_the_least_recently_seen_peer_goes_past_capacity() -> None:
    cache = MinPeerCache(2)

    await cache.add([1], _GROUP, 1)
    await cache.add([2], _GROUP, 2)
    # Seen again, so peer 2 is now the least recently seen one.
    await cache.add([1], _GROUP, 3)
    await cache.add([3], _GROUP, 4)

    assert 1 in cache
    assert 2 not in cache
    assert 3 in cache
    assert len(cache) == 2


async def test_one_message_records_every_peer_it_is_given() -> None:
    cache = MinPeerCache(10)

    await cache.add({_USER, _OTHER_USER}, _GROUP, 9)

    assert await cache.get(_USER) == [Sighting(_GROUP, 9)]
    assert await cache.get(_OTHER_USER) == [Sighting(_GROUP, 9)]


async def test_get_with_a_chat_gives_only_that_sighting() -> None:
    cache = MinPeerCache(10)

    await cache.add([_USER], _GROUP, 5)
    await cache.add([_USER], _OTHER_GROUP, 6)

    assert await cache.get(_USER, _GROUP) == [Sighting(_GROUP, 5)]
    assert await cache.get(_USER, _THIRD_GROUP) == []


async def test_get_hands_out_a_copy() -> None:
    # `resolve_peer` awaits a request per sighting while it walks this list, and new sightings
    #  or discards land in between. They must not change the list it is walking.
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)

    sightings = await cache.get(_USER)
    await cache.discard(_USER)

    assert sightings == [Sighting(_GROUP, 5)]


async def test_discard_with_only_the_peer_forgets_all_of_it() -> None:
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)
    await cache.add([_USER], _OTHER_GROUP, 6)

    await cache.discard(_USER)

    assert _USER not in cache


async def test_discard_with_a_chat_forgets_that_sighting_only() -> None:
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)
    await cache.add([_USER], _OTHER_GROUP, 6)

    await cache.discard(_USER, _GROUP)

    assert await cache.get(_USER) == [Sighting(_OTHER_GROUP, 6)]


async def test_discarding_the_last_sighting_forgets_the_peer() -> None:
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)

    await cache.discard(_USER, _GROUP, 5)

    assert _USER not in cache
    assert len(cache) == 0


async def test_discard_with_a_message_keeps_a_sighting_that_replaced_it() -> None:
    # A newer message may have been recorded in the same chat while the stale one was being
    #  tried. Forgetting the chat then would drop the newer, working sighting.
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)
    await cache.add([_USER], _GROUP, 8)

    await cache.discard(_USER, _GROUP, 5)

    assert await cache.get(_USER) == [Sighting(_GROUP, 8)]


async def test_discard_of_an_unknown_peer_or_chat_does_nothing() -> None:
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)

    await cache.discard(_OTHER_USER)
    await cache.discard(_USER, _OTHER_GROUP)

    assert await cache.get(_USER) == [Sighting(_GROUP, 5)]


async def test_discard_with_a_message_but_no_chat_is_rejected() -> None:
    # Message ids are only unique inside a chat.
    cache = MinPeerCache(10)

    with pytest.raises(ValueError, match="message_id needs a chat_id"):
        await cache.discard(_USER, None, 5)


async def test_discard_messages_with_only_the_chat_forgets_it_for_every_peer() -> None:
    cache = MinPeerCache(10)
    await cache.add([_USER, _OTHER_USER], _GROUP, 5)
    await cache.add([_USER], _OTHER_GROUP, 6)

    await cache.discard_messages(_GROUP)

    assert await cache.get(_USER) == [Sighting(_OTHER_GROUP, 6)]
    # Its only sighting is gone, so the peer is gone with it.
    assert _OTHER_USER not in cache


async def test_discard_messages_forgets_only_the_given_messages() -> None:
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)
    await cache.add([_OTHER_USER], _GROUP, 6)
    await cache.add([_USER], _OTHER_GROUP, 5)

    await cache.discard_messages(_GROUP, 5)

    # Message 5 of another chat is a different message.
    assert await cache.get(_USER) == [Sighting(_OTHER_GROUP, 5)]
    assert await cache.get(_OTHER_USER) == [Sighting(_GROUP, 6)]


async def test_discard_messages_takes_many_messages_at_once() -> None:
    cache = MinPeerCache(10)
    await cache.add([1], _GROUP, 5)
    await cache.add([2], _GROUP, 6)
    await cache.add([3], _GROUP, 7)

    await cache.discard_messages(_GROUP, iter([5, 6]))

    assert 1 not in cache
    assert 2 not in cache
    assert await cache.get(3) == [Sighting(_GROUP, 7)]


async def test_discard_messages_with_no_messages_forgets_nothing() -> None:
    # An empty collection is not the same as passing no messages, which means the whole chat.
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)

    await cache.discard_messages(_GROUP, [])

    assert await cache.get(_USER) == [Sighting(_GROUP, 5)]


async def test_reset_lock_keeps_the_sightings() -> None:
    cache = MinPeerCache(10)
    await cache.add([_USER], _GROUP, 5)
    lock = cache._lock

    cache.reset_lock()

    assert cache._lock is not lock
    assert await cache.get(_USER) == [Sighting(_GROUP, 5)]


def test_repr_shows_capacity_and_size() -> None:
    assert repr(MinPeerCache(10)) == "MinPeerCache(capacity=10, size=0)"

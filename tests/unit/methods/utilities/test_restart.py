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


"""`restart()` keeps what the caches hold.

It stops and starts the client, and `start()` rebuilds every primitive that binds to a
loop. The message and topic caches own one of those locks, so rebuilding the `Cache` object
instead of the lock alone would throw the cached messages away on every restart.
"""

from __future__ import annotations as _annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pyrogram import Client

_MESSAGE_KEY: Final[tuple[int, int]] = (-1001, 42)
_TOPIC_KEY: Final[tuple[int, int]] = (-1001, 7)


async def test_restart_keeps_the_message_and_topic_caches(offline_client: Client) -> None:
    await offline_client.start()

    await offline_client.message_cache.set(_MESSAGE_KEY, "a message")
    await offline_client.topic_cache.set(_TOPIC_KEY, "a topic")

    locks_before_restart = (offline_client.message_cache._lock, offline_client.topic_cache._lock)

    await offline_client.restart()

    try:
        assert await offline_client.message_cache.get(_MESSAGE_KEY) == "a message"
        assert await offline_client.topic_cache.get(_TOPIC_KEY) == "a topic"

        assert (
            offline_client.message_cache._lock,
            offline_client.topic_cache._lock,
        ) != locks_before_restart

    finally:
        await offline_client.stop()

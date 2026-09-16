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

"""`start()` records the loop it runs on, and rebuilds what binds to a loop.

`pyrogram/sync.py` needs a loop object to hand a coroutine to from a thread that is
running none of its own, and asyncio offers no way to ask another thread which loop it
drives.
"""

from __future__ import annotations as _annotations

import asyncio
import typing

import pytest

from pyrogram import Client


def stop_before_the_network() -> typing.NoReturn:
    """`start()` rebuilds the loop-bound primitives before it loads a plugin."""
    raise RuntimeError("far enough")


async def test_starting_a_client_records_the_loop_for_the_sync_bridge(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(client, "load_plugins", stop_before_the_network)

    with pytest.raises(RuntimeError, match="far enough"):
        await client.start()

    # The record is private and `pyrogram/sync.py` is its only reader.
    assert client._loop is asyncio.get_running_loop()


async def test_start_rebuilds_everything_that_binds_to_a_loop(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(client, "load_plugins", stop_before_the_network)

    built_by_the_constructor = [
        client.sessions_lock,
        client.save_file_semaphore,
        client.get_file_semaphore,
        client.updates_watchdog_event,
        client.message_cache._lock,
        client.topic_cache._lock,
    ]

    with pytest.raises(RuntimeError, match="far enough"):
        await client.start()

    built_by_start = [
        client.sessions_lock,
        client.save_file_semaphore,
        client.get_file_semaphore,
        client.updates_watchdog_event,
        client.message_cache._lock,
        client.topic_cache._lock,
    ]

    assert all(
        new is not old for new, old in zip(built_by_start, built_by_the_constructor, strict=True)
    )


def test_the_constructor_takes_no_loop() -> None:
    handed_loop = asyncio.new_event_loop()

    try:
        with pytest.raises(TypeError, match="unexpected keyword argument 'loop'"):
            Client(
                name="handed_loop_probe",
                in_memory=True,
                # The parameter being gone is the subject of this test, so `ty` reporting it
                #  as unknown is the same claim made statically.
                loop=handed_loop,  # ty: ignore[unknown-argument]
            )

    finally:
        handed_loop.close()

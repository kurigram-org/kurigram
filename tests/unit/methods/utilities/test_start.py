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

"""`start()` records the loop it runs on, and that record is the client's only one.

`pyrogram/sync.py` needs a loop object to hand a coroutine to from a thread that is
running none of its own, and asyncio offers no way to ask another thread which loop it
drives.
"""

from __future__ import annotations as _annotations

import asyncio
import typing

import pytest

from pyrogram import Client


@pytest.fixture
def client() -> Client:
    return Client(
        name="start_probe",
        in_memory=True,
    )


async def test_start_records_the_loop_it_is_running_on(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def stop_before_the_network() -> typing.NoReturn:
        raise RuntimeError("far enough")

    monkeypatch.setattr(client, "load_plugins", stop_before_the_network)

    with pytest.raises(RuntimeError, match="far enough"):
        await client.start()

    assert client.loop is asyncio.get_running_loop()


def test_a_loop_handed_to_the_constructor_is_refused() -> None:
    handed_loop = asyncio.new_event_loop()

    try:
        with pytest.warns(DeprecationWarning, match=r"Client\(loop=\.\.\.\) is ignored"):
            client = Client(
                name="handed_loop_probe",
                in_memory=True,
                loop=handed_loop,
            )

        assert client.loop is None

    finally:
        handed_loop.close()

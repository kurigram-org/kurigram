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


"""Fixtures for the lifecycle methods: a plain client, and one whose socket is gone.

`offline_client` replaces the four methods that reach the network and nothing else, so
`start()`, `stop()`, `initialize()`, `terminate()` and the dispatcher run for real. That is
the point: the state these tests are about is built by those methods, and a test that
patches them out cannot see it.
"""

from __future__ import annotations as _annotations

from dataclasses import dataclass
from typing import Any, Final

import pytest

from pyrogram import Client

_AUTH_KEY: Final[bytes] = bytes(256)
_DC_ID: Final[int] = 2


@dataclass(frozen=True, slots=True)
class _UpdateState:
    """What `start()` reads off `updates.GetState` before it stores an update state."""

    pts: int = 1
    qts: int = 1
    date: int = 1
    seq: int = 1


@pytest.fixture
def client() -> Client:
    return Client(
        name="lifecycle_probe",
        in_memory=True,
    )


@pytest.fixture
def offline_client(monkeypatch: pytest.MonkeyPatch) -> Client:
    client = Client(
        name="offline_lifecycle_probe",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
        workers=1,
    )

    # `load_session()` is not a stand-in for this: on an empty session it runs
    #  `Auth(...).create()`, which opens a socket.
    async def connect() -> bool:
        await client.storage.open()

        await client.storage.dc_id(_DC_ID)
        await client.storage.api_id(client.api_id)
        await client.storage.test_mode(False)
        await client.storage.auth_key(_AUTH_KEY)

        await client.storage.user_id(1)
        await client.storage.is_bot(False)
        await client.storage.date(0)

        client.is_connected = True

        return True

    async def disconnect() -> None:
        await client.storage.close()
        client.is_connected = False

    async def invoke(query: Any) -> _UpdateState:
        del query

        return _UpdateState()

    async def get_me() -> None:
        return None

    monkeypatch.setattr(client, "connect", connect)
    monkeypatch.setattr(client, "disconnect", disconnect)
    monkeypatch.setattr(client, "invoke", invoke)
    monkeypatch.setattr(client, "get_me", get_me)

    return client

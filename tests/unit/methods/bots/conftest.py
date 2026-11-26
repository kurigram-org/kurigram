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
"""A client that stops at its first request, so a test reads what a method built."""

from __future__ import annotations as _annotations

from typing import TYPE_CHECKING, NoReturn, Protocol

import pytest

from pyrogram import Client, raw, types

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from pyrogram.raw.core import TLObject


class _InvokeReached(Exception):
    """Raised by the patched `invoke`, carrying the request it was handed."""

    def __init__(self, query: TLObject) -> None:
        self._query = query

    @property
    def query(self) -> TLObject:
        return self._query


class Capture(Protocol):
    """Runs a method call to its `invoke` and returns the request, sending nothing."""

    async def __call__(self, call: Awaitable[types.Message | str | None], /) -> TLObject: ...


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Client:
    client = Client(
        name="request_probe",
        in_memory=True,
    )

    async def invoke(query: TLObject) -> NoReturn:
        raise _InvokeReached(query)

    async def resolve_peer(peer_id: int | str) -> raw.types.InputPeerUser:
        return raw.types.InputPeerUser(
            user_id=1,
            access_hash=1,
        )

    monkeypatch.setattr(client, "invoke", invoke)
    monkeypatch.setattr(client, "resolve_peer", resolve_peer)
    return client


@pytest.fixture
def capture() -> Capture:
    async def run(call: Awaitable[types.Message | str | None], /) -> TLObject:
        with pytest.raises(_InvokeReached) as reached:
            await call

        return reached.value.query

    return run

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

"""`Client.run()` drives `start`, `idle` and `stop` on one loop of its own.

It used to call `run_until_complete` three times on a loop the client kept, so the three
steps could land on a loop the application had never started.
"""

from __future__ import annotations as _annotations

import asyncio

import pytest

from pyrogram import Client
from pyrogram.methods.utilities import run as run_module


@pytest.fixture
def client() -> Client:
    return Client(
        name="run_probe",
        in_memory=True,
    )


def test_run_drives_start_idle_and_stop_on_one_loop_of_its_own(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[asyncio.AbstractEventLoop] = []

    async def record(*, use_qr: bool = False, except_ids: list[int] | None = None) -> None:
        del use_qr, except_ids

        seen.append(asyncio.get_running_loop())

    monkeypatch.setattr(client, "start", record)
    monkeypatch.setattr(client, "stop", record)
    monkeypatch.setattr(run_module, "idle", record)

    client.run()
    client.run()

    assert len(seen) == 6

    first_run, second_run = seen[:3], seen[3:]

    assert set(map(id, first_run)) == {id(first_run[0])}
    assert set(map(id, second_run)) == {id(second_run[0])}

    # `asyncio.run` owns the loop it made and closes it, so the second call cannot be
    #  handed the first one back.
    assert first_run[0].is_closed()
    assert second_run[0] is not first_run[0]


def test_run_hands_its_arguments_to_start(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: dict[str, bool | list[int] | None] = {}

    async def record_start(*, use_qr: bool, except_ids: list[int] | None) -> None:
        recorded["use_qr"] = use_qr
        recorded["except_ids"] = except_ids

    async def do_nothing() -> None:
        pass

    monkeypatch.setattr(client, "start", record_start)
    monkeypatch.setattr(client, "stop", do_nothing)
    monkeypatch.setattr(run_module, "idle", do_nothing)

    client.run(
        use_qr=True,
        except_ids=[7],
    )

    assert recorded == {"use_qr": True, "except_ids": [7]}

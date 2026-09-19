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

The first test runs the real `start()` and `stop()` against a client with no socket, rather
than patching them out. Patched out, nothing touches `updates_queue` or
`updates_watchdog_event`, and those are exactly what a second `run()` used to die on.
"""

from __future__ import annotations as _annotations

import asyncio
from typing import TYPE_CHECKING, Final

from pyrogram.methods.utilities import run as run_module

if TYPE_CHECKING:
    import pytest

    from pyrogram import Client

_OTHER_DC_ID: Final[int] = 4


class _CachedSession:
    """What `get_session()` leaves in `Client.sessions` for a DC that is not the current one."""

    def __init__(self) -> None:
        self.stopped: bool = False

    async def stop(self) -> None:
        self.stopped = True


def test_run_drives_start_idle_and_stop_on_one_loop_of_its_own(
    offline_client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    idle_loops: list[asyncio.AbstractEventLoop] = []
    loops_start_recorded: list[asyncio.AbstractEventLoop | None] = []

    async def record_the_loops() -> None:
        idle_loops.append(asyncio.get_running_loop())
        loops_start_recorded.append(offline_client._loop)

    monkeypatch.setattr(run_module, "idle", record_the_loops)

    offline_client.run()
    offline_client.run()

    first_loop, second_loop = idle_loops

    assert idle_loops == loops_start_recorded

    # `asyncio.run` owns the loop it made and closes it, so the second call cannot be
    #  handed the first one back.
    assert first_loop.is_closed()
    assert second_loop is not first_loop

    assert offline_client.is_initialized is False
    assert offline_client.is_connected is False


def test_run_stops_the_sessions_it_cached_before_the_loop_goes(
    offline_client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cached_session = _CachedSession()

    async def cache_a_session() -> None:
        offline_client.sessions[_OTHER_DC_ID] = cached_session

    monkeypatch.setattr(run_module, "idle", cache_a_session)

    offline_client.run()

    # `terminate()` used to stop `media_sessions` and leave these running: a session
    #  bound to the loop `run()` has just closed cannot serve the next `run()`, and its
    #  `recv` and `ping` tasks hold a socket until something stops them.
    assert cached_session.stopped is True
    assert offline_client.sessions == {}


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

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


"""The loop helpers take `uvloop` when it imports and fall back to `asyncio` when it does not.

`uvloop` is not installed in this environment, so both sides are pinned by patching the
module attribute the import left behind: `None` for the fallback, a recording stand-in for
the taken path. No test here needs `uvloop` itself, and none needs Windows to prove the
fallback: an absent import is the same state on every platform.
"""

from __future__ import annotations as _annotations

import asyncio
from typing import TYPE_CHECKING, Any

from pyrogram.utils import loops

if TYPE_CHECKING:
    from collections.abc import Coroutine

    import pytest


class _RecordingUvloop:
    """The two entry points `loops` reaches for, recording what they were handed."""

    def __init__(self) -> None:
        self.built_loops: list[asyncio.AbstractEventLoop] = []
        self.ran: list[Coroutine[Any, Any, None]] = []

    def new_event_loop(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        self.built_loops.append(loop)
        return loop

    def run(self, main: Coroutine[Any, Any, None]) -> None:
        self.ran.append(main)
        main.close()


def test_new_event_loop_without_uvloop_builds_a_plain_asyncio_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(loops, "uvloop", None)

    loop = loops.new_event_loop()

    assert isinstance(loop, asyncio.AbstractEventLoop)

    loop.close()


def test_new_event_loop_with_uvloop_hands_back_its_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recording_uvloop = _RecordingUvloop()
    monkeypatch.setattr(loops, "uvloop", recording_uvloop)

    loop = loops.new_event_loop()

    assert recording_uvloop.built_loops == [loop]

    loop.close()


def test_run_without_uvloop_drives_the_coroutine_on_a_fresh_asyncio_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(loops, "uvloop", None)

    driving_loops: list[asyncio.AbstractEventLoop] = []

    async def record_the_loop() -> None:
        driving_loops.append(asyncio.get_running_loop())

    loops.run(record_the_loop())

    # `asyncio.run` builds the loop, drives the coroutine to the end and closes what it built.
    assert len(driving_loops) == 1
    assert driving_loops[0].is_closed()


def test_run_with_uvloop_hands_the_coroutine_to_its_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recording_uvloop = _RecordingUvloop()
    monkeypatch.setattr(loops, "uvloop", recording_uvloop)

    async def do_nothing() -> None:
        pass

    coroutine = do_nothing()

    loops.run(coroutine)

    assert recording_uvloop.ran == [coroutine]

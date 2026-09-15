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

"""The sync bridge resolves both of its loops when the wrapped method runs, not at import.

`pyrogram.sync` wraps every client method and every bound method of every type while
`import pyrogram` is still running, so a loop resolved there is one nothing ever runs.
A sync call made off the client's loop was bridged to it and died with
`RuntimeError: ... got Future ... attached to a different loop`.
"""

from __future__ import annotations as _annotations

import asyncio
import os
import signal
import subprocess
import sys
import threading
import time
from collections.abc import AsyncGenerator, Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Final

import pytest

import pyrogram
from pyrogram import Client, utils
from pyrogram.sync import async_to_sync

_HANDLED_SIGNALS: Final[tuple[signal.Signals, ...]] = (
    signal.SIGINT,
    signal.SIGTERM,
    signal.SIGABRT,
)

_REPOSITORY_ROOT: Final[Path] = Path(__file__).parents[2]


class Api:
    """Reaches its client's loop the way `Session.send` does (`pyrogram/session/session.py:349`)."""

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self.executor = ThreadPoolExecutor(1, thread_name_prefix="Handler")

    async def shout(self, text: str) -> str:
        return await self.loop.run_in_executor(self.executor, str.upper, text)

    async def spell(self, text: str) -> AsyncGenerator[str]:
        for letter in text:
            yield await self.loop.run_in_executor(self.executor, str.upper, letter)


def _bridged(loop: asyncio.AbstractEventLoop) -> Api:
    api = Api(loop)

    async_to_sync(api, "shout")
    async_to_sync(api, "spell")

    return api


@pytest.fixture(autouse=True)
def forget_the_recorded_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    # `get_event_loop()` records the first loop it is asked from, and that record would
    #  otherwise outlive the test that made it and answer for the next one.
    monkeypatch.setattr(utils, "_loop", None)


@pytest.fixture
def sync_only_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """The loop `get_event_loop()` builds for a caller that is not inside one."""
    loop = utils.get_event_loop()

    yield loop

    loop.close()
    asyncio.set_event_loop(None)


def test_importing_pyrogram_resolves_no_loop() -> None:
    probe: str = "import pyrogram; from pyrogram import utils; print(utils._loop)"
    recorded = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        check=True,
        cwd=_REPOSITORY_ROOT,
        text=True,
    )

    assert recorded.stdout.strip() == "None"


def test_get_running_loop_answers_none_outside_a_loop_and_records_nothing() -> None:
    assert utils.get_running_loop() is None
    assert utils._loop is None


async def test_get_running_loop_answers_the_loop_the_caller_is_inside() -> None:
    assert utils.get_running_loop() is asyncio.get_running_loop()


async def test_get_event_loop_records_the_loop_it_is_first_asked_from() -> None:
    running = asyncio.get_running_loop()

    assert utils.get_event_loop() is running
    assert utils._loop is running


def test_get_event_loop_keeps_answering_the_loop_it_recorded(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    assert utils.get_event_loop() is sync_only_loop


async def test_a_call_made_inside_the_client_loop_is_awaited_by_the_caller() -> None:
    running = asyncio.get_running_loop()
    api = _bridged(running)

    # `Client.loop` does this during `start()`, which is what records the loop.
    utils.get_event_loop()

    assert await api.shout("hello") == "HELLO"


async def test_a_call_made_from_a_worker_thread_reaches_the_client_loop() -> None:
    running = asyncio.get_running_loop()
    api = _bridged(running)

    utils.get_event_loop()

    # `Client.executor` runs a sync handler here, with no loop of its own.
    with ThreadPoolExecutor(1, thread_name_prefix="Handler") as handler_thread:
        assert await running.run_in_executor(handler_thread, api.shout, "hello") == "HELLO"


async def test_an_async_generator_made_from_a_worker_thread_reaches_the_client_loop() -> None:
    running = asyncio.get_running_loop()
    api = _bridged(running)

    utils.get_event_loop()

    with ThreadPoolExecutor(1, thread_name_prefix="Handler") as handler_thread:
        letters = await running.run_in_executor(handler_thread, lambda: list(api.spell("ab")))

    assert letters == ["A", "B"]


def test_a_call_made_from_sync_code_with_no_loop_drives_the_one_it_is_given(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    api = _bridged(sync_only_loop)

    assert api.shout("world") == "WORLD"


def test_an_async_generator_made_from_sync_code_with_no_loop_yields_its_items(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    api = _bridged(sync_only_loop)

    assert list(api.spell("ab")) == ["A", "B"]


def test_a_client_keeps_the_loop_it_was_given(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    client = Client(
        name="loop_probe",
        in_memory=True,
        loop=sync_only_loop,
    )

    assert client.loop is sync_only_loop


def test_a_client_running_in_another_thread_is_reached_from_the_thread_without_a_loop() -> None:
    loop = asyncio.new_event_loop()
    api = _bridged(loop)
    running = threading.Event()

    def drive_the_loop() -> None:
        asyncio.set_event_loop(loop)
        # `Client.loop` is read from inside the loop during `start()`, and that is what
        #  tells the bridge which loop the client was given.
        loop.call_soon(utils.get_event_loop)
        loop.call_soon(running.set)
        loop.run_forever()

    thread = threading.Thread(
        target=drive_the_loop,
        name="Loop",
    )
    thread.start()
    running.wait()

    try:
        assert api.shout("hello") == "HELLO"

    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
        loop.close()


@pytest.fixture
def restore_the_signal_handlers() -> Iterator[None]:
    # `idle()` installs its own and never puts the previous ones back, so without this the
    #  rest of the session would run with `Ctrl-C` wired to a loop that has stopped.
    installed = {number: signal.getsignal(number) for number in _HANDLED_SIGNALS}

    yield

    for number, handler in installed.items():
        signal.signal(number, handler)


def test_idle_called_from_sync_code_runs_on_the_loop_it_resolves_and_stops_on_a_signal(
    sync_only_loop: asyncio.AbstractEventLoop,
    restore_the_signal_handlers: None,
) -> None:
    listening = signal.getsignal(signal.SIGINT)

    def interrupt_once_idle_is_listening() -> None:
        # `idle()` replaces the handler as its first step; interrupting before that would
        #  reach whatever `pytest` had installed and abort the run.
        while signal.getsignal(signal.SIGINT) is listening:
            time.sleep(0.01)

        os.kill(os.getpid(), signal.SIGINT)

    interrupter = threading.Thread(
        target=interrupt_once_idle_is_listening,
        name="Interrupter",
    )
    interrupter.start()

    try:
        # `idle` is declared `async def`, so `ty` sees a coroutine function here: it can't
        #  know `pyrogram.sync` has patched it into a blocking sync wrapper, which is the
        #  whole subject of this test.
        pyrogram.idle()  # ty: ignore[unused-awaitable]

    finally:
        interrupter.join()

    assert not sync_only_loop.is_running()

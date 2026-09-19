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

"""The sync bridge sends a call to the loop the object it was made on runs on.

`pyrogram.sync` wraps every client method and every bound method of every type while
`import pyrogram` is still running, so the loop cannot be resolved there. Resolving it from
a process-wide record instead answers for whichever client asked first, and hands an async
generator to the caller's loop while its coroutine sibling goes to the client's. Both end
in `RuntimeError: ... got Future ... attached to a different loop`.
"""

from __future__ import annotations as _annotations

import asyncio
import inspect
import os
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Final, Protocol

import pytest

import pyrogram
from pyrogram import Client, sync, types
from pyrogram.sync import _bridge_loop, async_to_sync

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterator

_HANDLED_SIGNALS: Final[tuple[signal.Signals, ...]] = (
    signal.SIGINT,
    signal.SIGTERM,
    signal.SIGABRT,
)

_REPOSITORY_ROOT: Final[Path] = Path(__file__).parents[2]


class Api:
    """A client stand-in: a private `_loop`, the shape `start()` leaves `Client` in."""

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self.executor = ThreadPoolExecutor(1, thread_name_prefix="Handler")

    async def running_loop(self) -> asyncio.AbstractEventLoop:
        return asyncio.get_running_loop()

    async def running_loops(self, count: int) -> AsyncGenerator[asyncio.AbstractEventLoop]:
        for _ in range(count):
            yield asyncio.get_running_loop()

    # `shout` and `spell` reach their own loop the way `Session.send` does
    #  (`pyrogram/session/session.py:349`), so running them anywhere else raises.
    async def shout(self, text: str) -> str:
        return await self._loop.run_in_executor(self.executor, str.upper, text)

    async def spell(self, text: str) -> AsyncGenerator[str]:
        for letter in text:
            yield await self._loop.run_in_executor(self.executor, str.upper, letter)


class Bound:
    """A bound method reaching its client the way every `types.Object` subclass does."""

    def __init__(self, client: Api) -> None:
        self._client = client

    async def shout(self, text: str) -> str:
        return await self._client._loop.run_in_executor(
            self._client.executor,
            str.upper,
            text,
        )


# The library wraps its methods on the class, at import, and so does this.
async_to_sync(Api, "running_loop")
async_to_sync(Api, "running_loops")
async_to_sync(Api, "shout")
async_to_sync(Api, "spell")

async_to_sync(Bound, "shout")


class LoopInAnotherThread(Protocol):
    def __call__(self, *, name: str) -> asyncio.AbstractEventLoop: ...


@pytest.fixture(autouse=True)
def forget_the_sync_caller_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    # The bridge keeps the loop it built for a caller that was inside none, and that loop
    #  would otherwise outlive the test that asked for it and answer for the next one.
    monkeypatch.setattr(sync, "_sync_caller_loop", None)


@pytest.fixture
def sync_only_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """The loop the bridge builds for a caller that is not inside one."""
    loop = sync._loop_for_sync_callers()

    yield loop

    loop.close()
    asyncio.set_event_loop(None)


@pytest.fixture
def idle_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """A loop nothing drives, standing in for a client that was given one of its own."""
    loop = asyncio.new_event_loop()

    yield loop

    loop.close()


@pytest.fixture
def loop_in_another_thread() -> Iterator[LoopInAnotherThread]:
    """Loops driven by threads of their own, the way a client started off this one is."""
    driven: list[tuple[asyncio.AbstractEventLoop, threading.Thread]] = []

    def start(*, name: str) -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        running = threading.Event()

        def drive() -> None:
            asyncio.set_event_loop(loop)
            loop.call_soon(running.set)
            loop.run_forever()

        thread = threading.Thread(
            target=drive,
            name=name,
        )
        thread.start()
        running.wait()

        driven.append((loop, thread))

        return loop

    yield start

    for loop, thread in driven:
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
        loop.close()


def _client_started_on(loop: asyncio.AbstractEventLoop, *, name: str) -> Client:
    """A client as starting it leaves it: carrying the loop it ran on."""
    client = Client(
        name=name,
        in_memory=True,
    )
    client._loop = loop

    return client


def test_importing_pyrogram_resolves_no_loop() -> None:
    probe: str = "import pyrogram; print(pyrogram.sync._sync_caller_loop)"
    recorded = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        check=True,
        cwd=_REPOSITORY_ROOT,
        text=True,
    )

    assert recorded.stdout.strip() == "None"


def test_the_running_loop_helper_answers_none_outside_a_loop_and_builds_nothing() -> None:
    assert sync._running_loop() is None
    assert sync._sync_caller_loop is None


async def test_the_running_loop_helper_answers_the_loop_the_caller_is_inside() -> None:
    assert sync._running_loop() is asyncio.get_running_loop()


def test_the_loop_built_for_a_caller_inside_none_is_kept_and_handed_back(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    assert sync._loop_for_sync_callers() is sync_only_loop


def test_the_bridge_takes_its_loop_from_the_object_the_call_is_made_on(
    idle_loop: asyncio.AbstractEventLoop,
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    client = _client_started_on(idle_loop, name="bridge_loop_probe")

    assert _bridge_loop((client,)) is idle_loop
    user = types.User(
        client=client,
        id=1,
    )

    assert _bridge_loop((user,)) is idle_loop

    # `idle()` and `compose()` are wrapped on their module, so no argument carries a loop.
    assert _bridge_loop(()) is sync_only_loop


def test_the_bridge_passes_over_a_loop_that_has_been_closed(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    """What `asyncio.run()` leaves behind: the loop it drove the client on, now closed."""
    spent = asyncio.new_event_loop()
    spent.close()

    api = Api(spent)

    assert _bridge_loop((api,)) is sync_only_loop
    assert api.running_loop() is sync_only_loop


async def test_a_call_made_inside_the_client_loop_is_awaited_by_the_caller() -> None:
    api = Api(asyncio.get_running_loop())

    assert await api.shout("hello") == "HELLO"


async def test_a_call_made_from_a_worker_thread_reaches_the_client_loop() -> None:
    running = asyncio.get_running_loop()
    api = Api(running)

    # `Client.executor` runs a sync handler here, with no loop of its own.
    with ThreadPoolExecutor(1, thread_name_prefix="Handler") as handler_thread:
        assert await running.run_in_executor(handler_thread, api.shout, "hello") == "HELLO"


async def test_an_async_generator_made_from_a_worker_thread_reaches_the_client_loop() -> None:
    running = asyncio.get_running_loop()
    api = Api(running)

    with ThreadPoolExecutor(1, thread_name_prefix="Handler") as handler_thread:
        letters = await running.run_in_executor(handler_thread, lambda: list(api.spell("ab")))

    assert letters == ["A", "B"]


async def test_a_call_made_on_a_bound_object_reaches_the_loop_of_the_client_it_carries(
    loop_in_another_thread: LoopInAnotherThread,
) -> None:
    client_loop = loop_in_another_thread(name="ClientLoop")

    assert await Bound(Api(client_loop)).shout("hello") == "HELLO"


async def test_a_call_made_from_another_loop_runs_on_the_client_loop(
    loop_in_another_thread: LoopInAnotherThread,
) -> None:
    client_loop = loop_in_another_thread(name="ClientLoop")
    api = Api(client_loop)

    assert await api.running_loop() is client_loop
    assert await api.shout("hello") == "HELLO"


async def test_an_async_generator_made_from_another_loop_runs_on_the_client_loop_too(
    loop_in_another_thread: LoopInAnotherThread,
) -> None:
    client_loop = loop_in_another_thread(name="ClientLoop")
    api = Api(client_loop)

    assert [loop async for loop in api.running_loops(2)] == [client_loop, client_loop]
    assert [letter async for letter in api.spell("ab")] == ["A", "B"]


async def test_closing_an_async_generator_made_from_another_loop_finishes_it(
    loop_in_another_thread: LoopInAnotherThread,
) -> None:
    client_loop = loop_in_another_thread(name="ClientLoop")
    letters = Api(client_loop).spell("abc")

    assert await anext(letters) == "A"

    await letters.aclose()

    with pytest.raises(StopAsyncIteration):
        await anext(letters)


async def test_a_call_from_another_loop_to_a_client_loop_nothing_drives_says_so(
    idle_loop: asyncio.AbstractEventLoop,
) -> None:
    api = Api(idle_loop)

    # Without this the call is handed to a loop nobody runs, and the caller waits forever.
    with pytest.raises(RuntimeError, match="belongs to an event loop that is not running"):
        await api.shout("hello")


def test_a_call_made_from_sync_code_with_no_loop_drives_the_one_it_is_given(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    api = Api(sync_only_loop)

    assert api.shout("world") == "WORLD"


def test_an_async_generator_made_from_sync_code_with_no_loop_yields_its_items(
    sync_only_loop: asyncio.AbstractEventLoop,
) -> None:
    api = Api(sync_only_loop)

    assert list(api.spell("ab")) == ["A", "B"]


def test_a_client_offers_no_loop_in_its_public_api() -> None:
    client = Client(
        name="loop_probe",
        in_memory=True,
    )

    # The record the sync bridge reads is private, and nothing hands one in: the client
    #  runs on the loop that runs it.
    assert client._loop is None
    assert not hasattr(client, "loop")
    assert "loop" not in inspect.signature(Client.__init__).parameters
    assert sync._sync_caller_loop is None


def test_a_second_client_started_on_its_own_loop_is_not_given_the_first_ones(
    loop_in_another_thread: LoopInAnotherThread,
) -> None:
    first_loop = loop_in_another_thread(name="FirstClientLoop")
    second_loop = loop_in_another_thread(name="SecondClientLoop")

    first = _client_started_on(first_loop, name="first_client_probe")
    second = _client_started_on(second_loop, name="second_client_probe")

    assert _bridge_loop((first,)) is first_loop
    assert _bridge_loop((second,)) is second_loop


def test_a_client_running_in_another_thread_is_reached_from_the_thread_without_a_loop(
    loop_in_another_thread: LoopInAnotherThread,
) -> None:
    api = Api(loop_in_another_thread(name="ClientLoop"))

    assert api.shout("hello") == "HELLO"


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

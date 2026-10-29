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

"""Registering a handler takes effect where it is called, whatever is running.

`add_handler` and `remove_handler` are ordinary synchronous methods, so the caller
decides when they happen. They used to schedule the work on a loop instead, which lost
every handler registered before the application started one. Being synchronous, they are
also called from whatever thread the caller is on, which is what the last test here covers.
"""

from __future__ import annotations as _annotations

import asyncio
import sys
import threading
from typing import TYPE_CHECKING, Any, Final, Protocol

import pytest

from pyrogram import Client, raw
from pyrogram.handlers import MessageHandler, RawUpdateHandler, StartHandler
from pyrogram.storage import UpdateState

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from pyrogram.handlers.handler import Handler
    from pyrogram.types import Message

_REGISTERING_THREADS: Final[int] = 2
_HANDLERS_PER_THREAD: Final[int] = 500
_UPDATES_SENT: Final[int] = 3

# `UpdateShort` reaches the queue without touching storage, and no parser claims the
#  inner update, so a worker hands it to a raw handler untouched.
_UNPARSED_UPDATE: Final[raw.types.UpdateShort] = raw.types.UpdateShort(
    update=raw.types.UpdateDcOptions(dc_options=[]),
    date=0,
)


# The dispatcher calls a handler callback positionally.
async def greet(client: Client, message: Message, /) -> None:
    pass


@pytest.fixture
def client() -> Client:
    return Client(
        name="dispatcher_probe",
        in_memory=True,
    )


@pytest.fixture
def client_without_updates() -> Client:
    """`no_updates` keeps `Dispatcher.start()` off the network: no workers, no gap recovery."""
    return Client(
        name="dispatcher_probe",
        in_memory=True,
        no_updates=True,
    )


def test_a_handler_registered_outside_a_loop_survives_into_one(client: Client) -> None:
    handler = MessageHandler(greet)

    client.add_handler(handler)

    async def registered() -> dict[int, list[Handler[Any]]]:
        return client.dispatcher.groups

    assert asyncio.run(registered()) == {0: [handler]}


def test_groups_are_dispatched_lowest_first(client: Client) -> None:
    last = MessageHandler(greet)
    first = MessageHandler(greet)

    client.add_handler(last, group=3)
    client.add_handler(first, group=-1)

    assert list(client.dispatcher.groups) == [-1, 3]


def _recording_handler(group: int, *, fired: list[int]) -> RawUpdateHandler:
    """A raw handler that notes the group it was registered in, once it runs."""

    async def record(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        fired.append(group)

    return RawUpdateHandler(record)


async def test_a_lower_group_is_dispatched_before_a_higher_one(client: Client) -> None:
    """What the sort in `add_handler` is for, read off a dispatch rather than off the keys."""
    fired: list[int] = []

    client.add_handler(_recording_handler(3, fired=fired), group=3)
    client.add_handler(_recording_handler(-1, fired=fired), group=-1)

    dispatcher = client.dispatcher

    # An update no parser claims, so the worker reaches the handlers with it untouched and
    #  needs neither the network nor a session.
    dispatcher.updates_queue.put_nowait((raw.types.UpdateDcOptions(dc_options=[]), {}, {}))
    dispatcher.updates_queue.put_nowait(None)

    await dispatcher.handler_worker()

    assert fired == [-1, 3]


def test_remove_handler_takes_the_group_with_its_last_handler(client: Client) -> None:
    handler = MessageHandler(greet)

    client.add_handler(handler, group=2)
    client.remove_handler(handler, group=2)

    assert client.dispatcher.groups == {}


def test_remove_handler_reports_a_group_that_was_never_added(client: Client) -> None:
    with pytest.raises(ValueError, match="Group 7 does not exist"):
        client.remove_handler(MessageHandler(greet), group=7)


def test_registering_leaves_a_mapping_already_being_read_alone(client: Client) -> None:
    dispatching = MessageHandler(greet)
    client.add_handler(dispatching)

    # What a worker mid-update holds: rebuilding the mapping under it must not be seen
    #  by this iteration, nor raise `RuntimeError: dictionary changed size during iteration`.
    groups = iter(client.dispatcher.groups.values())
    handlers = next(groups)

    client.add_handler(MessageHandler(greet), group=1)
    client.add_handler(MessageHandler(greet))

    assert list(groups) == []
    assert handlers == [dispatching]


async def test_start_rebuilds_the_queue_for_the_loop_about_to_read_it(
    client_without_updates: Client,
) -> None:
    dispatcher = client_without_updates.dispatcher
    built_by_the_constructor = dispatcher.updates_queue

    await dispatcher.start()

    assert dispatcher.updates_queue is not built_by_the_constructor


async def test_an_update_is_dropped_while_no_worker_runs(client: Client) -> None:
    """A client that only called `connect()`: nothing drains the queue, so nothing enters it."""
    for _ in range(_UPDATES_SENT):
        await client.handle_updates(_UNPARSED_UPDATE)

    assert client.dispatcher.updates_queue.qsize() == 0


async def test_a_started_dispatcher_delivers_every_update(client: Client) -> None:
    fired: list[int] = []
    client.add_handler(_recording_handler(0, fired=fired))

    await client.dispatcher.start()

    for _ in range(_UPDATES_SENT):
        await client.handle_updates(_UNPARSED_UPDATE)

    await client.dispatcher.stop()

    assert fired == [0] * _UPDATES_SENT


async def test_an_update_after_stop_is_dropped(client: Client) -> None:
    await client.dispatcher.start()
    await client.dispatcher.stop(clear_handlers=False)

    await client.handle_updates(_UNPARSED_UPDATE)

    assert client.dispatcher.updates_queue.qsize() == 0


async def test_an_update_during_the_start_callback_is_delivered(client: Client) -> None:
    """The network delivers while `start_handler` runs; the workers start only after it."""
    fired: list[int] = []
    client.add_handler(_recording_handler(0, fired=fired))

    async def receive(client: Client, /) -> None:
        await client.handle_updates(_UNPARSED_UPDATE)

    client.add_handler(StartHandler(receive))

    await client.dispatcher.start()
    await client.dispatcher.stop()

    assert fired == [0]


async def test_an_update_while_stop_is_pending_is_dropped(client: Client) -> None:
    handling = asyncio.Event()
    released = asyncio.Event()

    async def hold(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        handling.set()
        await released.wait()

    client.add_handler(RawUpdateHandler(hold))

    await client.dispatcher.start()
    await client.handle_updates(_UNPARSED_UPDATE)
    await handling.wait()

    # One yield lets `stop()` queue its sentinels while every worker is still busy.
    stopping = asyncio.create_task(client.dispatcher.stop(clear_handlers=False))
    await asyncio.sleep(0)

    await client.handle_updates(_UNPARSED_UPDATE)
    released.set()
    await stopping

    assert client.dispatcher.updates_queue.qsize() == 0


async def test_a_restart_keeping_handlers_runs_only_the_new_workers(client: Client) -> None:
    fired: list[int] = []
    client.add_handler(_recording_handler(0, fired=fired))

    await client.dispatcher.start()
    await client.dispatcher.stop(clear_handlers=False)

    assert client.dispatcher.handler_worker_tasks == []

    await client.dispatcher.start()
    await client.handle_updates(_UNPARSED_UPDATE)
    await client.dispatcher.stop(clear_handlers=False)

    assert client.dispatcher.handler_worker_tasks == []
    assert fired == [0]


async def test_a_started_client_without_updates_queues_nothing(
    client_without_updates: Client,
) -> None:
    """`start()` spawns no worker under `no_updates`, so admission stays closed."""
    await client_without_updates.dispatcher.start()

    await client_without_updates.handle_updates(_UNPARSED_UPDATE)

    assert client_without_updates.dispatcher.updates_queue.qsize() == 0


class _Route(Protocol):
    """Feeds the client one way an update reaches `Dispatcher.enqueue()`."""

    async def __call__(self, client: Client, /) -> None: ...


# Answers every `GetDifference` with one message and one other update, so a route
#  through a difference reaches both of its `enqueue()` calls.
_DIFFERENCE: Final[raw.types.updates.Difference] = raw.types.updates.Difference(
    new_messages=[raw.types.MessageEmpty(id=1)],
    new_encrypted_messages=[],
    other_updates=[raw.types.UpdateDcOptions(dc_options=[])],
    chats=[],
    users=[],
    state=raw.types.updates.State(
        pts=2,
        qts=0,
        date=1,
        seq=1,
        unread_count=0,
    ),
)


async def _answer_with_difference(query: raw.core.TLObject, /) -> raw.types.updates.Difference:
    return _DIFFERENCE


async def _send_updates_container(client: Client, /) -> None:
    updates = raw.types.Updates(
        updates=[raw.types.UpdateDcOptions(dc_options=[])],
        users=[],
        chats=[],
        date=1,
        seq=1,
    )
    await client.handle_updates(updates)


async def _send_short_message(client: Client, /) -> None:
    short_message = raw.types.UpdateShortMessage(
        id=1,
        user_id=1,
        message="",
        pts=2,
        pts_count=1,
        date=1,
    )
    await client.handle_updates(short_message)


async def _recover_a_gap(client: Client, /) -> None:
    await client.storage.set_update_state(UpdateState(0, 1, None, 1, 1))
    await client.recover_gaps()


_ROUTES: Final[tuple[Any, ...]] = (
    pytest.param(_send_updates_container, ["UpdateDcOptions"], id="updates-container"),
    pytest.param(
        _send_short_message,
        ["UpdateDcOptions", "UpdateNewMessage"],
        id="short-message-difference",
    ),
    pytest.param(
        _recover_a_gap,
        ["UpdateDcOptions", "UpdateNewMessage"],
        id="recovered-difference",
    ),
)


@pytest.fixture
async def client_with_storage(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[Client]:
    """Peers and update states are written on every route, and `invoke` stays offline."""
    monkeypatch.setattr(client, "invoke", _answer_with_difference)
    await client.storage.open()

    yield client

    await client.storage.close()


@pytest.mark.parametrize(("route", "delivered"), _ROUTES)
async def test_every_route_drops_while_no_worker_runs(
    client_with_storage: Client,
    route: _Route,
    delivered: list[str],
) -> None:
    await route(client_with_storage)

    assert client_with_storage.dispatcher.updates_queue.qsize() == 0


@pytest.mark.parametrize(("route", "delivered"), _ROUTES)
async def test_every_route_delivers_once_started(
    client_with_storage: Client,
    route: _Route,
    delivered: list[str],
) -> None:
    received: list[str] = []

    async def record(
        client: Client,
        update: raw.base.Update,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
        /,
    ) -> None:
        received.append(type(update).__name__)

    client_with_storage.add_handler(RawUpdateHandler(record))

    await client_with_storage.dispatcher.start()
    await route(client_with_storage)
    await client_with_storage.dispatcher.stop()

    assert sorted(received) == delivered


@pytest.fixture
def frequent_thread_switches() -> Generator[None]:
    """Switch threads inside the copy-and-rebind rather than around it.

    The default interval is 5ms, which is far longer than a registration takes, so two
    threads interleave inside one only by luck.
    """
    previous = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)

    try:
        yield

    finally:
        sys.setswitchinterval(previous)


@pytest.mark.usefixtures("frequent_thread_switches")
def test_handlers_registered_from_two_threads_at_once_all_survive(client: Client) -> None:
    def register() -> None:
        for _ in range(_HANDLERS_PER_THREAD):
            client.add_handler(MessageHandler(greet))

    threads = [threading.Thread(target=register) for _ in range(_REGISTERING_THREADS)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    registered = sum(len(handlers) for handlers in client.dispatcher.groups.values())

    assert registered == _HANDLERS_PER_THREAD * _REGISTERING_THREADS

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
from typing import TYPE_CHECKING, Final

import pytest

from pyrogram import Client
from pyrogram.handlers import MessageHandler

if TYPE_CHECKING:
    from collections import OrderedDict
    from collections.abc import Iterator

    from pyrogram.types import Message

_REGISTERING_THREADS: Final[int] = 2
_HANDLERS_PER_THREAD: Final[int] = 500


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

    async def registered() -> OrderedDict[int, list[MessageHandler]]:
        return client.dispatcher.groups

    assert asyncio.run(registered()) == {0: [handler]}


def test_groups_are_dispatched_lowest_first(client: Client) -> None:
    last = MessageHandler(greet)
    first = MessageHandler(greet)

    client.add_handler(last, group=3)
    client.add_handler(first, group=-1)

    assert list(client.dispatcher.groups) == [-1, 3]


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


@pytest.fixture
def frequent_thread_switches() -> Iterator[None]:
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

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

"""Parsing a message records where its `min` peers were seen, for `resolve_peer` to use."""

from __future__ import annotations as _annotations

from typing import Final

import pytest

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.utils.cache import Sighting

_GROUP: Final[int] = 1234567
_USER: Final[int] = 777001
_DATE: Final[int] = 1755100000

_GROUP_ID: Final[int] = utils.get_channel_id(_GROUP)


def a_client(*, is_bot: bool = False) -> pyrogram.Client:
    # A user account would fetch the topic of a service message from the server otherwise.
    client = pyrogram.Client(
        "test", api_id=1, api_hash="0" * 32, in_memory=True, fetch_topics=False
    )
    # As on a started client, so the account kind is not read from the unopened storage.
    client.me = types.User(id=1, is_bot=is_bot)

    return client


def a_supergroup() -> raw.types.Channel:
    return raw.types.Channel(
        id=_GROUP,
        title="Group",
        photo=raw.types.ChatPhotoEmpty(),
        date=_DATE,
        megagroup=True,
        access_hash=555,
        usernames=[],
        restriction_reason=[],
    )


def a_sender(*, is_min: bool) -> raw.types.User:
    return raw.types.User(
        id=_USER,
        min=is_min,
        access_hash=1,
        first_name="u",
        usernames=[],
        restriction_reason=[],
    )


def a_message() -> raw.types.Message:
    return raw.types.Message(
        id=42,
        peer_id=raw.types.PeerChannel(channel_id=_GROUP),
        from_id=raw.types.PeerUser(user_id=_USER),
        date=_DATE,
        message="hi",
        entities=[],
        restriction_reason=[],
    )


def a_service_message() -> raw.types.MessageService:
    return raw.types.MessageService(
        id=43,
        peer_id=raw.types.PeerChannel(channel_id=_GROUP),
        from_id=raw.types.PeerUser(user_id=_USER),
        date=_DATE,
        action=raw.types.MessageActionChatEditTitle(title="New title"),
    )


async def parse(
    client: pyrogram.Client,
    message: raw.base.Message,
    *,
    is_min: bool = True,
    is_scheduled: bool = False,
) -> types.Message:
    return await types.Message._parse(
        client,
        message,
        users={_USER: a_sender(is_min=is_min)},
        chats={_GROUP: a_supergroup()},
        is_scheduled=is_scheduled,
        replies=0,
    )


@pytest.mark.parametrize(
    ("message", "message_id"),
    [(a_message(), 42), (a_service_message(), 43)],
)
async def test_a_min_sender_is_recorded_with_the_message(
    message: raw.base.Message, message_id: int
) -> None:
    client = a_client()

    await parse(client, message)

    assert await client.min_peer_cache.get(_USER) == [Sighting(_GROUP_ID, message_id)]


async def test_a_full_sender_is_not_recorded() -> None:
    # Its `access_hash` is stored, `resolve_peer` never needs a message for it.
    client = a_client()

    await parse(client, a_message(), is_min=False)

    assert len(client.min_peer_cache) == 0


async def test_a_scheduled_message_is_not_recorded() -> None:
    client = a_client()

    await parse(client, a_message(), is_scheduled=True)

    assert len(client.min_peer_cache) == 0


async def test_a_bot_records_nothing() -> None:
    client = a_client(is_bot=True)

    await parse(client, a_message())

    assert len(client.min_peer_cache) == 0

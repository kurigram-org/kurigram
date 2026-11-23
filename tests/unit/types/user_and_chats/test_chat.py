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

from __future__ import annotations as _annotations

from typing import Final

import pytest

import pyrogram
from pyrogram import enums, raw, types

_USER_ID: Final[int] = 777000
_CHANNEL_ID: Final[int] = 2


@pytest.mark.asyncio
async def test_an_ephemeral_message_without_a_peer_takes_its_chat_from_the_sender() -> None:
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )
    sender = raw.types.User(
        id=_USER_ID,
        first_name="Sender",
        access_hash=0,
    )

    # `peer_id` is optional on `ephemeralMessage`; the user id used to be looked up in
    #  `chats`, so the chat came back `None`.
    message = raw.types.EphemeralMessage(
        id=1,
        from_id=raw.types.PeerUser(user_id=_USER_ID),
        receiver_id=1,
        date=0,
        message="hi",
    )

    chat = await types.Chat._parse(
        client,
        message,
        users={_USER_ID: sender},
        chats={},
        is_chat=True,
    )

    assert chat is not None
    assert (chat.id, chat.type) == (_USER_ID, enums.ChatType.PRIVATE)


@pytest.mark.asyncio
async def test_a_sender_of_another_peer_kind_than_the_chat_is_looked_up_as_its_own_kind() -> None:
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )
    channel = raw.types.Channel(
        id=_CHANNEL_ID,
        title="Sender channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        access_hash=0,
        usernames=[],
        restriction_reason=[],
    )

    # A channel posting in a basic group: the channel id was looked up as a basic group,
    #  which raised `AttributeError: 'Channel' object has no attribute 'deactivated'`.
    message = raw.types.Message(
        id=1,
        peer_id=raw.types.PeerChat(chat_id=1),
        from_id=raw.types.PeerChannel(channel_id=_CHANNEL_ID),
        date=0,
        message="hi",
    )

    chat = await types.Chat._parse(
        client,
        message,
        users={},
        chats={_CHANNEL_ID: channel},
        is_chat=False,
    )

    assert chat is not None
    assert (chat.id, chat.type) == (-1000000000000 - _CHANNEL_ID, enums.ChatType.CHANNEL)

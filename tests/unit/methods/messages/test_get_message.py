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

from pyrogram import raw
from pyrogram.errors import MessageIdInvalid
from pyrogram.methods.messages.get_message import GetMessage
from pyrogram.methods.messages.get_messages import GetMessages
from pyrogram.utils import Cache

_CHAT_ID: Final[int] = 7
_MESSAGE_ID: Final[int] = 99


class Answerer(GetMessage, GetMessages):
    """A client that answers `messages.GetMessages` with a fixed vector and resolves any peer."""

    # `get_message()` reaches `get_messages()` through the real mixin rather than a stub, because
    #  the delegation is the only thing this method does and nothing else checks it: no overload
    #  of `get_messages()` accepts the fully optional union forwarded to it, so `ty` resolves the
    #  call to `Unknown` and a renamed keyword would type-check clean.

    def __init__(self, messages: list[raw.base.Message]) -> None:
        self.messages = messages
        self.message_cache = Cache(16)
        self._queries: list[raw.core.TLObject] = []

    @property
    def queries(self) -> list[raw.core.TLObject]:
        return self._queries

    async def resolve_peer(self, peer_id: int | str) -> raw.types.InputPeerChat:
        return raw.types.InputPeerChat(chat_id=_CHAT_ID)

    async def invoke(
        self,
        query: raw.core.TLObject,
        *,
        sleep_threshold: int = 0,
    ) -> raw.types.messages.Messages:
        self._queries.append(query)

        return raw.types.messages.Messages(
            messages=self.messages,
            chats=[a_chat()],
            users=[],
            topics=[],
        )


def a_chat() -> raw.types.Chat:
    return raw.types.Chat(
        id=_CHAT_ID,
        title="A chat",
        photo=None,
        participants_count=2,
        date=0,
        version=1,
    )


def a_message(*, reply_to: raw.base.MessageReplyHeader | None = None) -> raw.types.Message:
    # `entities` and `restriction_reason` are `flags.N?Vector<...>`, and the generated `read()`
    #  gives an absent vector back as `[]`. `Message._parse()` iterates both without guarding, so
    #  a hand-built `raw.types.Message` has to spell out what the wire implies.
    return raw.types.Message(
        id=_MESSAGE_ID,
        peer_id=raw.types.PeerChat(chat_id=_CHAT_ID),
        date=0,
        message="A message",
        reply_to=reply_to,
        entities=[],
        restriction_reason=[],
    )


@pytest.mark.asyncio
async def test_an_answer_with_no_message_raises() -> None:
    # An empty vector is what `get_messages()` turns into `None`.
    with pytest.raises(MessageIdInvalid) as raised:
        await Answerer([]).get_message(
            chat_id=_CHAT_ID,
            message_id=_MESSAGE_ID,
        )

    assert raised.value.value == _MESSAGE_ID


@pytest.mark.asyncio
async def test_a_deleted_message_raises() -> None:
    # What the server actually sends for a deleted message, or for an id nobody ever used, is a
    #  `messageEmpty` in the vector rather than no element at all. `get_messages()` parses it into
    #  a `Message` with `empty` set, which a check for `None` alone handed straight back.
    with pytest.raises(MessageIdInvalid) as raised:
        await Answerer([raw.types.MessageEmpty(id=_MESSAGE_ID)]).get_message(
            chat_id=_CHAT_ID,
            message_id=_MESSAGE_ID,
        )

    assert raised.value.value == _MESSAGE_ID


@pytest.mark.asyncio
async def test_a_message_that_exists_is_handed_straight_back() -> None:
    message = await Answerer([a_message()]).get_message(
        chat_id=_CHAT_ID,
        message_id=_MESSAGE_ID,
    )

    assert message.id == _MESSAGE_ID
    assert message.text == "A message"


@pytest.mark.asyncio
async def test_the_replies_asked_for_reach_get_messages() -> None:
    # `get_messages()` fetches the replied message with a second call unless `replies` is 0, and
    #  its own default is 1, so a `replies` that never reached it still answered and only cost a
    #  call the caller had declined.
    client = Answerer([a_message(reply_to=raw.types.MessageReplyHeader(reply_to_msg_id=98))])

    await client.get_message(
        chat_id=_CHAT_ID,
        message_id=_MESSAGE_ID,
        replies=0,
    )

    assert len(client.queries) == 1

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
from pyrogram.client import Cache
from pyrogram.errors import MessageIdInvalid
from pyrogram.methods.messages.get_message import GetMessage
from pyrogram.methods.messages.get_messages import GetMessages

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

    async def resolve_peer(self, peer_id: int | str) -> raw.types.InputPeerChat:
        return raw.types.InputPeerChat(chat_id=_CHAT_ID)

    async def invoke(
        self,
        query: raw.core.TLObject,
        *,
        sleep_threshold: int = 0,
    ) -> raw.types.messages.Messages:
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


def a_message() -> raw.types.Message:
    # `entities` and `restriction_reason` are `flags.N?Vector<...>`, and the generated `read()`
    #  gives an absent vector back as `[]`. `Message._parse()` iterates both without guarding, so
    #  a hand-built `raw.types.Message` has to spell out what the wire implies.
    return raw.types.Message(
        id=_MESSAGE_ID,
        peer_id=raw.types.PeerChat(chat_id=_CHAT_ID),
        date=0,
        message="A message",
        entities=[],
        restriction_reason=[],
    )


@pytest.mark.asyncio
async def test_a_message_that_does_not_exist_raises() -> None:
    # Telegram answers with an empty vector for an id nobody ever used, and for one whose message
    #  has since been deleted. `get_messages()` turns that into `None`.
    with pytest.raises(MessageIdInvalid) as raised:
        await Answerer([]).get_message(
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

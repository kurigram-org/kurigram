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

from pyrogram import enums, raw, types
from pyrogram.methods.messages.send_chat_action import SendChatAction, _ACTIONS

_INTERACTION: Final[str] = '{"v": 1, "a": [{"i": 1, "t": 0.0}]}'


class FakeClient(SendChatAction):
    """A client that captures the raw action built for `messages.SetTyping`."""

    def __init__(self) -> None:
        self.captured: raw.base.SendMessageAction | None = None

    async def resolve_peer(self, peer_id: int) -> raw.types.InputPeerUser:
        return raw.types.InputPeerUser(
            user_id=peer_id,
            access_hash=0,
        )

    async def invoke(
        self,
        query: raw.functions.messages.SetTyping,
        *,
        business_connection_id: str | None = None,
    ) -> bool:
        del business_connection_id

        self.captured = query.action
        return True


@pytest.mark.parametrize(
    "action",
    [pytest.param(member, id=member.name.lower().replace("_", "-")) for member in enums.ChatAction],
)
async def test_every_enum_member_resolves_to_its_raw_action(action: enums.ChatAction) -> None:
    # `_ACTIONS` is a hand-written map from every `enums.ChatAction` member to its raw
    #  constructor; parametrizing over the enum itself is what makes a member added
    #  without a map entry fail here instead of surfacing as a KeyError at call time.
    client = FakeClient()

    result = await client.send_chat_action(
        chat_id=7,
        action=action,
    )

    assert result is True
    assert isinstance(client.captured, action.value)


def test_the_actions_map_holds_no_stale_entries() -> None:
    assert set(_ACTIONS) == set(enums.ChatAction)


async def test_a_chat_action_instance_is_sent_as_it_writes_itself() -> None:
    client = FakeClient()

    result = await client.send_chat_action(
        chat_id=7,
        action=types.ChatActionEmojiInteraction(
            "👍",
            message_id=1234,
            interaction=_INTERACTION,
        ),
    )

    assert result is True

    # `TLObject.__eq__` walks `self.__slots__` only, so an action with no fields compares
    #  equal to anything: the type is asserted separately rather than through the value.
    assert type(client.captured) is raw.types.SendMessageEmojiInteraction
    assert client.captured == raw.types.SendMessageEmojiInteraction(
        emoticon="👍",
        msg_id=1234,
        interaction=raw.types.DataJSON(data=_INTERACTION),
    )


async def test_a_chat_action_instance_carries_the_fields_the_caller_chose() -> None:
    client = FakeClient()

    result = await client.send_chat_action(
        chat_id=7,
        action=types.ChatActionUploadVideo(progress=42),
    )

    assert result is True

    assert type(client.captured) is raw.types.SendMessageUploadVideoAction
    assert client.captured == raw.types.SendMessageUploadVideoAction(progress=42)

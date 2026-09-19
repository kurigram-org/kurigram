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

import re
from typing import Final

import pytest

from pyrogram import enums, raw
from pyrogram.methods.messages.send_chat_action import (
    SendChatAction,
    _ACTIONS,
    _FIELD_ACTIONS,
)

_INTERACTION: Final[str] = '{"v": 1, "a": [{"i": 1, "t": 0.0}]}'


class FakeClient(SendChatAction):
    """A client that captures the raw action built for `messages.SetTyping`."""

    def __init__(self) -> None:
        self.captured = None

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=peer_id, access_hash=0)

    async def invoke(self, query: raw.functions.messages.SetTyping, **kwargs):
        self.captured = query.action
        return True


@pytest.mark.asyncio
@pytest.mark.parametrize("action", list(_ACTIONS))
async def test_every_chat_action_resolves_to_its_raw_action(action) -> None:
    # `_ACTIONS` is a hand-written map from every argument-less `enums.ChatAction` member to
    #  its raw constructor; the test below is what makes a member added to neither table fail
    #  instead of surfacing as a KeyError at call time.
    client = FakeClient()

    result = await client.send_chat_action(chat_id=7, action=action)

    assert result is True
    assert isinstance(client.captured, action.value)


def test_actions_map_covers_every_enum_member() -> None:
    assert set(_ACTIONS) | set(_FIELD_ACTIONS) == set(enums.ChatAction)
    assert not set(_ACTIONS) & set(_FIELD_ACTIONS)


@pytest.mark.asyncio
async def test_emoji_interaction_carries_the_emoticon_the_message_and_the_payload() -> None:
    client = FakeClient()

    result = await client.send_chat_action(
        chat_id=7,
        action=enums.ChatAction.EMOJI_INTERACTION,
        emoticon="👍",
        message_id=1234,
        interaction=_INTERACTION,
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


@pytest.mark.asyncio
async def test_emoji_interaction_seen_carries_only_the_emoticon() -> None:
    client = FakeClient()

    result = await client.send_chat_action(
        chat_id=7,
        action=enums.ChatAction.EMOJI_INTERACTION_SEEN,
        emoticon="👍",
    )

    assert result is True

    assert type(client.captured) is raw.types.SendMessageEmojiInteractionSeen
    assert client.captured == raw.types.SendMessageEmojiInteractionSeen(emoticon="👍")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("action", "fields", "expected"),
    [
        pytest.param(
            enums.ChatAction.EMOJI_INTERACTION,
            {},
            "ChatAction.EMOJI_INTERACTION needs emoticon, interaction, message_id",
            id="interaction-nothing-given",
        ),
        pytest.param(
            enums.ChatAction.EMOJI_INTERACTION,
            {"emoticon": "👍"},
            "ChatAction.EMOJI_INTERACTION needs interaction, message_id",
            id="interaction-emoticon-only",
        ),
        pytest.param(
            enums.ChatAction.EMOJI_INTERACTION_SEEN,
            {},
            "ChatAction.EMOJI_INTERACTION_SEEN needs emoticon",
            id="seen-nothing-given",
        ),
    ],
)
async def test_an_emoji_interaction_without_its_fields_names_what_is_missing(
    action: enums.ChatAction,
    fields: dict[str, str | int],
    expected: str,
) -> None:
    client = FakeClient()

    with pytest.raises(ValueError, match=re.escape(expected)):
        await client.send_chat_action(
            chat_id=7,
            action=action,
            **fields,
        )

    assert client.captured is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("action", "fields", "expected"),
    [
        pytest.param(
            enums.ChatAction.TYPING,
            {"emoticon": "👍"},
            "ChatAction.TYPING takes no emoticon",
            id="typing-emoticon",
        ),
        pytest.param(
            enums.ChatAction.UPLOAD_PHOTO,
            {"message_id": 1234, "interaction": _INTERACTION},
            "ChatAction.UPLOAD_PHOTO takes no interaction, message_id",
            id="upload-photo-message-and-payload",
        ),
        pytest.param(
            enums.ChatAction.EMOJI_INTERACTION_SEEN,
            {"emoticon": "👍", "message_id": 1234},
            "ChatAction.EMOJI_INTERACTION_SEEN takes no message_id",
            id="seen-message-id",
        ),
    ],
)
async def test_an_action_given_fields_it_does_not_take_names_them(
    action: enums.ChatAction,
    fields: dict[str, str | int],
    expected: str,
) -> None:
    client = FakeClient()

    with pytest.raises(ValueError, match=re.escape(expected)):
        await client.send_chat_action(
            chat_id=7,
            action=action,
            **fields,
        )

    assert client.captured is None

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
from pyrogram.types.messages_and_media.message import Str

CHANNEL_ID = 1000000000
USER_ID = 777000
DATE = 1755100000
_BUTTON_URL: Final[str] = "https://example.com"


def client():
    return pyrogram.Client("test", api_id=1, api_hash="0" * 32, in_memory=True)


def monoforum_chat():
    return raw.types.Channel(
        id=CHANNEL_ID,
        title="Direct messages",
        photo=raw.types.ChatPhotoEmpty(),
        date=DATE,
        broadcast=True,
        monoforum=True,
        access_hash=0,
        usernames=[],
        restriction_reason=[],
    )


def message(*, id=1, saved_peer_id=None, reply_to_msg_id=None):
    return raw.types.Message(
        id=id,
        peer_id=raw.types.PeerChannel(channel_id=CHANNEL_ID),
        from_id=raw.types.PeerUser(user_id=USER_ID),
        saved_peer_id=saved_peer_id,
        reply_to=(
            raw.types.MessageReplyHeader(reply_to_msg_id=reply_to_msg_id)
            if reply_to_msg_id is not None
            else None
        ),
        date=DATE,
        message="hi",
        entities=[],
        restriction_reason=[],
    )


@pytest.mark.asyncio
async def test_a_direct_message_without_a_topic_parses():
    parsed = await types.Message._parse(
        client(), message(), users={}, chats={CHANNEL_ID: monoforum_chat()}
    )

    assert parsed.chat.type == enums.ChatType.DIRECT
    assert parsed.direct_messages_topic_id is None
    assert parsed.topic is None


@pytest.mark.asyncio
async def test_a_direct_message_with_a_topic_keeps_its_id():
    parsed = await types.Message._parse(
        client(),
        message(saved_peer_id=raw.types.PeerUser(user_id=USER_ID)),
        users={},
        chats={CHANNEL_ID: monoforum_chat()},
    )

    assert parsed.direct_messages_topic_id == USER_ID


# The chat is missing from `chats` when Telegram sends an update without the peer it
#  happened in (a "min" or otherwise unresolved peer), so `Message.chat` comes out None.
#  Parsing must still produce a message instead of raising `AttributeError`.


@pytest.mark.asyncio
async def test_a_message_whose_chat_is_missing_parses_without_a_chat():
    parsed = await types.Message._parse(client(), message(), users={}, chats={})

    assert parsed.chat is None
    assert parsed.text == "hi"


@pytest.mark.asyncio
async def test_a_reply_whose_chat_is_missing_keeps_the_reply_id():
    parsed = await types.Message._parse(
        client(), message(id=2, reply_to_msg_id=1), users={}, chats={}
    )

    assert parsed.chat is None
    assert parsed.reply_to_message_id == 1
    assert parsed.reply_to_message is None


@pytest.mark.asyncio
async def test_a_service_reply_whose_chat_is_missing_parses():
    service = raw.types.MessageService(
        id=2,
        peer_id=raw.types.PeerChannel(channel_id=CHANNEL_ID),
        date=DATE,
        action=raw.types.MessageActionPinMessage(),
        reply_to=raw.types.MessageReplyHeader(reply_to_msg_id=1),
    )

    parsed = await types.Message._parse(client(), service, users={}, chats={})

    assert parsed.chat is None
    assert parsed.service == enums.MessageServiceType.PINNED_MESSAGE
    assert parsed.reply_to_message_id == 1


@pytest.mark.asyncio
async def test_a_reply_in_a_known_chat_is_still_taken_from_the_message_cache():
    shared_client = client()
    chats = {CHANNEL_ID: monoforum_chat()}

    await types.Message._parse(shared_client, message(id=1), users={}, chats=chats)
    parsed = await types.Message._parse(
        shared_client, message(id=2, reply_to_msg_id=1), users={}, chats=chats
    )

    assert parsed.reply_to_message is not None
    assert parsed.reply_to_message.id == 1


def message_with_url_button(label: str) -> types.Message:
    keyboard = types.InlineKeyboardMarkup(
        [[types.InlineKeyboardButton(label, url=_BUTTON_URL)]],
    )

    return types.Message(
        id=1,
        reply_markup=keyboard,
    )


@pytest.mark.asyncio
async def test_a_button_is_found_by_its_label() -> None:
    keyboard_message = message_with_url_button("Open")

    assert await keyboard_message.click("Open") == _BUTTON_URL


@pytest.mark.asyncio
async def test_an_unknown_button_label_names_the_label() -> None:
    keyboard_message = message_with_url_button("Open")

    with pytest.raises(ValueError, match="The button with label 'Close' doesn't exist"):
        await keyboard_message.click("Close")


@pytest.mark.asyncio
async def test_an_unknown_button_index_names_the_index() -> None:
    keyboard_message = message_with_url_button("Open")

    with pytest.raises(ValueError, match="The button at index 9 doesn't exist"):
        await keyboard_message.click(9)


_EMOJI_TEXT: Final[str] = "😀 250"


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        pytest.param(0, "😀", id="leading-half"),
        pytest.param(1, "😀", id="trailing-half"),
        pytest.param(2, " ", id="after-the-pair"),
        pytest.param(-1, "0", id="from-the-end"),
    ],
)
def test_an_index_inside_a_surrogate_pair_gives_the_whole_code_point(
    item: int,
    *,
    expected: str,
) -> None:
    assert Str(_EMOJI_TEXT)[item] == expected


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        pytest.param(slice(0, 1), "😀", id="leading-half-only"),
        pytest.param(slice(1, 2), "😀", id="trailing-half-only"),
        pytest.param(slice(0, 2), "😀", id="the-whole-pair"),
        pytest.param(slice(1, 3), "😀 ", id="opening-inside-the-pair"),
        pytest.param(slice(2, None), " 250", id="past-the-pair"),
        pytest.param(slice(None, None, -1), "052 😀", id="reversed"),
    ],
)
def test_a_slice_cutting_a_surrogate_pair_widens_to_the_whole_code_point(
    item: slice,
    *,
    expected: str,
) -> None:
    assert Str(_EMOJI_TEXT)[item] == expected


def test_an_entity_offset_still_indexes_the_text_that_entity_marks() -> None:
    entity = types.MessageEntity(
        type=enums.MessageEntityType.BOLD,
        offset=3,
        length=4,
    )
    text = Str("😀 bold").init([entity])

    assert text[entity.offset : entity.offset + entity.length] == "bold"

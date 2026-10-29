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

"""Which peers of a parsed message `get_message_min_peer_ids` hands to the sighting cache.

`None` means the message cannot address a `min` peer at all, a set (empty or not) means it can.
"""

from __future__ import annotations as _annotations

from typing import Final

import pytest

from pyrogram import enums, types
from pyrogram.utils import get_message_min_peer_ids

_GROUP_ID: Final[int] = -1001234567890
_MIN_USER_ID: Final[int] = 42
_MIN_CHANNEL_ID: Final[int] = -1009876543210


class _Storage:
    """Answers `is_bot()` with a fixed value, or fails if it is read when it must not be."""

    def __init__(self, is_bot: bool | None) -> None:
        self._is_bot = is_bot

    async def is_bot(self) -> bool:
        if self._is_bot is None:
            pytest.fail("the storage was read although `me` is known")

        return self._is_bot


class FakeClient:
    def __init__(self, *, me: types.User | None, storage_is_bot: bool | None = None) -> None:
        self.me = me
        self.storage = _Storage(storage_is_bot)


def a_user_client() -> FakeClient:
    return FakeClient(me=types.User(id=1, is_bot=False))


def a_group(chat_type: enums.ChatType = enums.ChatType.SUPERGROUP) -> types.Chat:
    return types.Chat(id=_GROUP_ID, type=chat_type)


def a_min_user(user_id: int = _MIN_USER_ID) -> types.User:
    return types.User(id=user_id, is_min=True)


def a_min_channel(chat_id: int = _MIN_CHANNEL_ID) -> types.Chat:
    return types.Chat(id=chat_id, type=enums.ChatType.CHANNEL, is_min=True)


def a_mention(user: types.User) -> types.MessageEntity:
    return types.MessageEntity(
        type=enums.MessageEntityType.TEXT_MENTION, offset=0, length=1, user=user
    )


def a_message(**kwargs) -> types.Message:
    kwargs.setdefault("chat", a_group())
    return types.Message(id=7, **kwargs)


@pytest.mark.parametrize(
    "chat_type",
    [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.FORUM],
)
async def test_a_channel_or_supergroup_message_is_usable(chat_type: enums.ChatType) -> None:
    message = a_message(chat=a_group(chat_type), from_user=a_min_user())

    assert await get_message_min_peer_ids(a_user_client(), message) == {_MIN_USER_ID}


@pytest.mark.parametrize(
    "chat_type",
    [
        enums.ChatType.PRIVATE,
        enums.ChatType.BOT,
        enums.ChatType.GROUP,
        # A monoforum: `users.getUsers` lists `CHANNEL_MONOFORUM_UNSUPPORTED`.
        enums.ChatType.DIRECT,
    ],
)
async def test_a_message_in_any_other_chat_is_not_usable(chat_type: enums.ChatType) -> None:
    message = a_message(chat=a_group(chat_type), from_user=a_min_user())

    assert await get_message_min_peer_ids(a_user_client(), message) is None


async def test_a_scheduled_message_is_not_usable() -> None:
    # Its id is not the id of a message in the chat.
    message = a_message(from_user=a_min_user(), scheduled=True)

    assert await get_message_min_peer_ids(a_user_client(), message) is None


async def test_a_message_without_a_chat_is_not_usable() -> None:
    message = types.Message(id=7, from_user=a_min_user())

    assert await get_message_min_peer_ids(a_user_client(), message) is None


async def test_a_bot_records_nothing() -> None:
    # Bots get `FROM_MESSAGE_BOT_DISABLED` for the `*FromMessage` constructors.
    client = FakeClient(me=types.User(id=1, is_bot=True))

    assert await get_message_min_peer_ids(client, a_message(from_user=a_min_user())) is None


async def test_without_me_the_account_kind_comes_from_the_storage() -> None:
    message = a_message(from_user=a_min_user())

    assert await get_message_min_peer_ids(FakeClient(me=None, storage_is_bot=True), message) is None
    assert await get_message_min_peer_ids(FakeClient(me=None, storage_is_bot=False), message) == {
        _MIN_USER_ID
    }


async def test_me_is_used_without_reading_the_storage() -> None:
    # `_Storage(None)` fails the test if it is read.
    client = FakeClient(me=types.User(id=1, is_bot=False), storage_is_bot=None)

    assert await get_message_min_peer_ids(client, a_message(from_user=a_min_user())) == {
        _MIN_USER_ID
    }


async def test_a_usable_message_without_min_peers_gives_an_empty_set() -> None:
    # Not `None`: the message itself is usable, it only references nobody worth recording.
    message = a_message(from_user=types.User(id=_MIN_USER_ID, is_min=False))

    assert await get_message_min_peer_ids(a_user_client(), message) == set()


async def test_the_sender_chat_is_recorded_when_there_is_no_sender_user() -> None:
    message = a_message(sender_chat=a_min_channel())

    assert await get_message_min_peer_ids(a_user_client(), message) == {_MIN_CHANNEL_ID}


async def test_a_channel_posting_in_itself_is_not_a_sighting() -> None:
    message = a_message(sender_chat=a_min_channel(_GROUP_ID))

    assert await get_message_min_peer_ids(a_user_client(), message) == set()


@pytest.mark.parametrize(
    ("origin", "expected"),
    [
        (types.MessageOriginUser(sender_user=a_min_user(50)), {50}),
        (types.MessageOriginChat(sender_chat=a_min_channel(-1005)), {-1005}),
        (types.MessageOriginChannel(chat=a_min_channel(-1006), message_id=3), {-1006}),
        # These carry a name only, nothing to address.
        (types.MessageOriginHiddenUser(sender_user_name="hidden"), set()),
        (types.MessageOriginImport(sender_user_name="imported"), set()),
    ],
)
async def test_the_forward_origin_is_recorded(
    origin: types.MessageOrigin, expected: set[int]
) -> None:
    message = a_message(forward_origin=origin)

    assert await get_message_min_peer_ids(a_user_client(), message) == expected


async def test_text_mentions_in_the_text_and_the_caption_are_recorded() -> None:
    message = a_message(
        entities=[
            a_mention(a_min_user(51)),
            types.MessageEntity(type=enums.MessageEntityType.BOLD, offset=0, length=1),
        ],
        caption_entities=[a_mention(a_min_user(52))],
    )

    assert await get_message_min_peer_ids(a_user_client(), message) == {51, 52}


async def test_every_source_together_gives_each_peer_once() -> None:
    message = a_message(
        from_user=a_min_user(),
        forward_origin=types.MessageOriginUser(sender_user=a_min_user()),
        entities=[a_mention(a_min_user()), a_mention(types.User(id=60, is_min=False))],
    )

    assert await get_message_min_peer_ids(a_user_client(), message) == {_MIN_USER_ID}

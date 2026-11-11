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

from pyrogram import raw, types

_USER_ID: Final[int] = 777000
_CHANNEL_ID: Final[int] = 1000000000

_USER: Final[raw.types.User] = raw.types.User(
    id=_USER_ID,
    first_name="Sender",
)
_CHANNEL: Final[raw.types.Channel] = raw.types.Channel(
    id=_CHANNEL_ID,
    title="Gifts",
    photo=raw.types.ChatPhotoEmpty(),
    date=0,
    broadcast=True,
    usernames=[],
    restriction_reason=[],
)

_USER_PEER: Final[raw.types.PeerUser] = raw.types.PeerUser(user_id=_USER_ID)
_CHANNEL_PEER: Final[raw.types.PeerChannel] = raw.types.PeerChannel(channel_id=_CHANNEL_ID)

# The Bot API form of a channel id: `-100` prepended to the raw one.
_CHANNEL_CHAT_ID: Final[int] = -1001000000000


# Both used to go through `User._parse`, so a channel came back `None` and a user as a
#  `User` where the annotation promises a `Chat`.
@pytest.mark.parametrize(
    ("sender_id", "recipient_id", "expected_ids"),
    [
        pytest.param(_USER_PEER, _CHANNEL_PEER, [_USER_ID, _CHANNEL_CHAT_ID], id="user-to-channel"),
        pytest.param(_CHANNEL_PEER, _USER_PEER, [_CHANNEL_CHAT_ID, _USER_ID], id="channel-to-user"),
    ],
)
async def test_sender_and_receiver_parse_as_chats_from_users_or_chats(
    sender_id: raw.base.Peer,
    *,
    recipient_id: raw.base.Peer,
    expected_ids: list[int],
) -> None:
    parsed = await types.UpgradedGiftOriginalDetails._parse(
        None,
        raw.types.StarGiftAttributeOriginalDetails(
            sender_id=sender_id,
            recipient_id=recipient_id,
            date=0,
        ),
        {_USER_ID: _USER},
        {_CHANNEL_ID: _CHANNEL},
    )
    chats = [parsed.sender, parsed.receiver]

    assert all(isinstance(chat, types.Chat) for chat in chats)
    assert [chat.id for chat in chats] == expected_ids


async def test_an_absent_sender_parses_to_none() -> None:
    parsed = await types.UpgradedGiftOriginalDetails._parse(
        None,
        raw.types.StarGiftAttributeOriginalDetails(
            recipient_id=_USER_PEER,
            date=0,
        ),
        {_USER_ID: _USER},
        {},
    )

    assert parsed.sender is None

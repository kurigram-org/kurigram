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

_RAW_ID: Final[int] = 7


@pytest.mark.parametrize(
    ("peer", "expected"),
    [
        pytest.param(
            raw.types.PeerChannel(channel_id=_RAW_ID),
            (None, enums.ChatType.CHANNEL),
            id="channel",
        ),
        pytest.param(
            raw.types.PeerUser(user_id=_RAW_ID),
            (_RAW_ID, None),
            id="user",
        ),
    ],
)
@pytest.mark.asyncio
async def test_the_poster_is_looked_up_by_the_peer_type(
    peer: raw.base.Peer,
    *,
    expected: tuple[int | None, enums.ChatType | None],
) -> None:
    # User and channel ids overlap, so a lookup by raw id alone took the channel for the user.
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )
    user = raw.types.User(
        id=_RAW_ID,
        first_name="User",
        access_hash=0,
    )
    channel = raw.types.Channel(
        id=_RAW_ID,
        title="Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=1,
        broadcast=True,
        access_hash=0,
        usernames=[],
        restriction_reason=[],
    )
    story = raw.types.StoryItem(
        id=1,
        date=1,
        expire_date=2,
        media=raw.types.MessageMediaEmpty(),
        media_areas=[],
    )

    parsed = await types.Story._parse(
        client,
        story,
        peer,
        {_RAW_ID: user},
        {_RAW_ID: channel},
    )

    assert (
        parsed.from_user.id if parsed.from_user else None,
        parsed.sender_chat.type if parsed.sender_chat else None,
    ) == expected

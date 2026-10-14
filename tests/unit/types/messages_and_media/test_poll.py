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

_USER_ID: Final[int] = 3
_CHANNEL_ID: Final[int] = 7


@pytest.mark.asyncio
async def test_a_channel_among_recent_voters_is_parsed_as_a_channel() -> None:
    poll = raw.types.MessageMediaPoll(
        poll=raw.types.Poll(
            id=1,
            question=raw.types.TextWithEntities(
                text="Question",
                entities=[],
            ),
            answers=[
                raw.types.PollAnswer(
                    text=raw.types.TextWithEntities(
                        text="Answer",
                        entities=[],
                    ),
                    option=b"0",
                ),
            ],
            hash=0,
        ),
        results=raw.types.PollResults(
            results=[
                raw.types.PollAnswerVoters(
                    option=b"0",
                    voters=2,
                    recent_voters=[
                        raw.types.PeerUser(user_id=_USER_ID),
                        raw.types.PeerChannel(channel_id=_CHANNEL_ID),
                    ],
                ),
            ],
            total_voters=2,
            recent_voters=[],
        ),
    )
    user = raw.types.User(
        id=_USER_ID,
        first_name="User",
        usernames=[],
        restriction_reason=[],
    )
    channel = raw.types.Channel(
        id=_CHANNEL_ID,
        title="Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        broadcast=True,
        access_hash=1,
        usernames=[],
        restriction_reason=[],
    )
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    parsed = await types.Poll._parse(
        client,
        poll,
        users={_USER_ID: user},
        chats={_CHANNEL_ID: channel},
    )

    recent_voters = parsed.options[0].recent_voters

    assert recent_voters is not None
    assert [voter.type for voter in recent_voters] == [
        enums.ChatType.PRIVATE,
        enums.ChatType.CHANNEL,
    ]


@pytest.mark.asyncio
async def test_a_channel_sharing_its_raw_id_with_a_user_is_still_parsed_as_the_channel() -> None:
    # User, chat and channel ids overlap, so a lookup by raw id alone picks the wrong entity.
    #  https://core.telegram.org/api/peers
    poll = raw.types.MessageMediaPoll(
        poll=raw.types.Poll(
            id=1,
            question=raw.types.TextWithEntities(
                text="Question",
                entities=[],
            ),
            answers=[
                raw.types.PollAnswer(
                    text=raw.types.TextWithEntities(
                        text="Answer",
                        entities=[],
                    ),
                    option=b"0",
                    added_by=raw.types.PeerUser(user_id=_CHANNEL_ID),
                ),
            ],
            hash=0,
        ),
        results=raw.types.PollResults(
            results=[
                raw.types.PollAnswerVoters(
                    option=b"0",
                    voters=1,
                    recent_voters=[raw.types.PeerChannel(channel_id=_CHANNEL_ID)],
                ),
            ],
            total_voters=1,
            recent_voters=[],
        ),
    )
    user = raw.types.User(
        id=_CHANNEL_ID,
        first_name="User",
        usernames=[],
        restriction_reason=[],
    )
    channel = raw.types.Channel(
        id=_CHANNEL_ID,
        title="Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=0,
        broadcast=True,
        access_hash=1,
        usernames=[],
        restriction_reason=[],
    )
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    parsed = await types.Poll._parse(
        client,
        poll,
        users={_CHANNEL_ID: user},
        chats={_CHANNEL_ID: channel},
    )

    option = parsed.options[0]

    assert option.recent_voters is not None
    assert [voter.type for voter in option.recent_voters] == [enums.ChatType.CHANNEL]

    assert option.added_by_user is not None
    assert option.added_by_user.id == _CHANNEL_ID
    assert option.added_by_chat is None

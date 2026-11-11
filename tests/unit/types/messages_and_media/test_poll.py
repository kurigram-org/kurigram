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

from pyrogram import enums, raw, types


async def test_a_channel_recent_voter_parses_beside_a_user_one() -> None:
    # The channel voter used to be looked up in `users` only and came back as `None`.
    media_poll = raw.types.MessageMediaPoll(
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
                )
            ],
            hash=0,
            public_voters=True,
        ),
        results=raw.types.PollResults(
            results=[
                raw.types.PollAnswerVoters(
                    option=b"0",
                    voters=2,
                    recent_voters=[
                        raw.types.PeerUser(user_id=10),
                        raw.types.PeerChannel(channel_id=20),
                    ],
                )
            ],
            total_voters=2,
        ),
    )

    poll = await types.Poll._parse(
        None,
        media_poll,
        users={
            10: raw.types.User(
                id=10,
                first_name="Voter",
                usernames=[],
                restriction_reason=[],
            )
        },
        chats={
            20: raw.types.Channel(
                id=20,
                title="Channel",
                photo=raw.types.ChatPhotoEmpty(),
                date=0,
                broadcast=True,
                usernames=[],
                restriction_reason=[],
            )
        },
    )

    recent_voters = poll.options[0].recent_voters

    assert recent_voters is not None
    assert [(voter.id, voter.type) for voter in recent_voters] == [
        (10, enums.ChatType.PRIVATE),
        (-1000000000020, enums.ChatType.CHANNEL),
    ]

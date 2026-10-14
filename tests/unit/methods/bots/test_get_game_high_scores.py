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
from .conftest import (
    CLIENT_SLEEP_THRESHOLD,
    INLINE_MESSAGE_DC_ID,
    INLINE_MESSAGE_ID,
    RAW_INLINE_MESSAGE_ID,
    GameClient,
)

_HIGH_SCORES: Final[raw.types.messages.HighScores] = raw.types.messages.HighScores(
    scores=[
        raw.types.HighScore(
            pos=1,
            user_id=7,
            score=1000,
        )
    ],
    users=[raw.types.User(id=7)],
)


@pytest.mark.asyncio
async def test_inline_high_scores_come_from_the_inline_message_dc() -> None:
    client = GameClient(response=_HIGH_SCORES)

    result = await client.get_game_high_scores(7, inline_message_id=INLINE_MESSAGE_ID)

    assert [(score.user.id, score.score, score.position) for score in result] == [(7, 1000, 1)]
    assert client.requested_sessions == [(INLINE_MESSAGE_DC_ID, True)]
    assert client.session.sent == [
        (
            raw.functions.messages.GetInlineGameHighScores(
                id=RAW_INLINE_MESSAGE_ID,
                user_id=raw.types.InputUser(
                    user_id=7,
                    access_hash=0,
                ),
            ).write(),
            CLIENT_SLEEP_THRESHOLD,
        )
    ]


@pytest.mark.asyncio
async def test_chat_high_scores_keep_the_positional_call() -> None:
    client = GameClient(response=_HIGH_SCORES)

    result = await client.get_game_high_scores(7, 100, 5)

    assert [(score.user.id, score.score, score.position) for score in result] == [(7, 1000, 1)]
    assert client.requested_sessions == []
    assert client.session.sent == [
        (
            raw.functions.messages.GetGameHighScores(
                peer=raw.types.InputUser(
                    user_id=100,
                    access_hash=0,
                ),
                id=5,
                user_id=raw.types.InputUser(
                    user_id=7,
                    access_hash=0,
                ),
            ).write(),
            None,
        )
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message_ids",
    [
        pytest.param({}, id="neither"),
        pytest.param({"chat_id": 100}, id="chat_id_only"),
        pytest.param({"message_id": 5}, id="message_id_only"),
    ],
)
async def test_without_a_full_message_id_raises(message_ids: dict[str, int]) -> None:
    client = GameClient(response=_HIGH_SCORES)

    with pytest.raises(ValueError, match="chat_id and message_id are required"):
        await client.get_game_high_scores(7, **message_ids)

    assert client.session.sent == []

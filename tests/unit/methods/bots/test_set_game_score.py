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

import pytest

from pyrogram import raw
from .conftest import (
    CLIENT_SLEEP_THRESHOLD,
    INLINE_MESSAGE_DC_ID,
    INLINE_MESSAGE_ID,
    RAW_INLINE_MESSAGE_ID,
    GameClient,
)


@pytest.mark.asyncio
async def test_inline_score_goes_to_the_inline_message_dc() -> None:
    client = GameClient(response=True)

    result = await client.set_game_score(
        user_id=7,
        score=1000,
        inline_message_id=INLINE_MESSAGE_ID,
    )

    assert result is True
    assert client.requested_sessions == [(INLINE_MESSAGE_DC_ID, True)]
    assert client.session.sent == [
        (
            raw.functions.messages.SetInlineGameScore(
                id=RAW_INLINE_MESSAGE_ID,
                user_id=raw.types.InputUser(
                    user_id=7,
                    access_hash=0,
                ),
                score=1000,
                edit_message=True,
            ).write(),
            CLIENT_SLEEP_THRESHOLD,
        )
    ]


@pytest.mark.asyncio
async def test_inline_forced_score_without_message_edit() -> None:
    client = GameClient(response=True)

    await client.set_game_score(
        user_id=7,
        score=25,
        force=True,
        disable_edit_message=True,
        inline_message_id=INLINE_MESSAGE_ID,
    )

    assert client.session.sent == [
        (
            raw.functions.messages.SetInlineGameScore(
                id=RAW_INLINE_MESSAGE_ID,
                user_id=raw.types.InputUser(
                    user_id=7,
                    access_hash=0,
                ),
                score=25,
                force=True,
                edit_message=False,
            ).write(),
            CLIENT_SLEEP_THRESHOLD,
        )
    ]

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

from pyrogram import raw, types
from pyrogram.errors import EmptyObjectError


@pytest.mark.asyncio
async def test_parse_chat_raises_on_chat_empty() -> None:
    with pytest.raises(EmptyObjectError, match="ChatEmpty"):
        await types.Chat._parse_chat(None, raw.types.ChatEmpty(id=7))


@pytest.mark.parametrize(
    ("emoji_status", "expected"),
    [
        pytest.param(raw.types.EmojiStatusEmpty(), None, id="empty"),
        pytest.param(raw.types.EmojiStatus(document_id=5), "5", id="custom-emoji"),
    ],
)
@pytest.mark.asyncio
async def test_parse_chat_maps_only_a_full_emoji_status(
    emoji_status: raw.base.EmojiStatus,
    *,
    expected: str | None,
) -> None:
    user = raw.types.User(
        id=7,
        first_name="User 7",
        usernames=[],
        restriction_reason=[],
        emoji_status=emoji_status,
    )

    chat = await types.Chat._parse_chat(None, user)

    assert getattr(chat.emoji_status, "custom_emoji_id", None) == expected

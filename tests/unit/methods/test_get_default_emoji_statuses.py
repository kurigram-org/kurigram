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

from typing import cast

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.methods.users.get_default_emoji_statuses import GetDefaultEmojiStatuses


class Answerer(GetDefaultEmojiStatuses):
    """A client that answers `account.GetDefaultEmojiStatuses` with fixed statuses."""

    def __init__(self, statuses: list[raw.base.EmojiStatus]) -> None:
        self._statuses = statuses

    async def invoke(self, query: raw.core.TLObject) -> raw.types.account.EmojiStatuses:
        return raw.types.account.EmojiStatuses(
            hash=0,
            statuses=self._statuses,
        )


@pytest.mark.asyncio
async def test_an_empty_status_keeps_its_place_as_nothing() -> None:
    # `EmojiStatus._parse()` reads `document_id`, which `emojiStatusEmpty` does not carry.
    client = cast(
        "pyrogram.Client",
        Answerer([raw.types.EmojiStatus(document_id=5), raw.types.EmojiStatusEmpty()]),
    )

    statuses = await client.get_default_emoji_statuses()

    assert [getattr(status, "custom_emoji_id", None) for status in statuses] == ["5", None]

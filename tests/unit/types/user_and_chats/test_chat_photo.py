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

from pyrogram import enums, raw, types


@pytest.mark.asyncio
async def test_a_markup_only_photo_reaches_the_sticker_branch() -> None:
    # `animation` is parsed one line above `sticker`, and used to raise on a markup-only photo,
    #  so the sticker branch that handles exactly this shape was unreachable.
    photo = raw.types.Photo(
        id=1,
        access_hash=2,
        file_reference=b"\x03",
        date=0,
        sizes=[
            raw.types.PhotoSize(
                type="x",
                w=640,
                h=640,
                size=1024,
            )
        ],
        dc_id=2,
        video_sizes=[
            raw.types.VideoSizeEmojiMarkup(
                emoji_id=5,
                background_colors=[1],
            )
        ],
    )

    parsed = await types.ChatPhoto._parse(None, photo, 7, 8)

    assert parsed.animation is None

    assert parsed.sticker is not None
    assert parsed.sticker.type is enums.ChatPhotoStickerType.CUSTOM_EMOJI
    assert parsed.sticker.custom_emoji_id == "5"

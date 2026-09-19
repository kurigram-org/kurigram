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


def _photo(video_sizes: list[raw.base.VideoSize]) -> raw.types.Photo:
    return raw.types.Photo(
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
        video_sizes=video_sizes,
    )


@pytest.mark.asyncio
async def test_markup_only_video_sizes_parse_to_none() -> None:
    # `VideoSize` is a union, so a photo whose every entry is a markup constructor clears the
    #  `photo.video_sizes` guard and filters down to nothing. `max()` used to raise there:
    #  `ValueError: max() iterable argument is empty`.
    photo = _photo(
        [
            raw.types.VideoSizeEmojiMarkup(
                emoji_id=5,
                background_colors=[1],
            )
        ]
    )

    assert await types.AnimatedChatPhoto._parse(None, photo) is None


@pytest.mark.asyncio
async def test_the_largest_concrete_video_size_wins_over_markup_entries() -> None:
    photo = _photo(
        [
            raw.types.VideoSizeEmojiMarkup(
                emoji_id=5,
                background_colors=[1],
            ),
            raw.types.VideoSize(
                type="u",
                w=100,
                h=100,
                size=10,
                video_start_ts=0.5,
            ),
            raw.types.VideoSize(
                type="v",
                w=1280,
                h=1280,
                size=9000,
                video_start_ts=1.5,
            ),
        ]
    )

    parsed = await types.AnimatedChatPhoto._parse(None, photo)

    assert parsed is not None
    assert parsed.length == 1280
    assert parsed.main_frame_timestamp == pytest.approx(1.5)

    assert parsed.animation.width == 1280
    assert parsed.animation.height == 1280
    assert parsed.animation.file_size == 9000

    assert parsed.animation.file_id == "AgACAgIAAwEDAAIBAAcCAA8BAAMCAAN2AAceBA"
    assert parsed.animation.file_unique_id == "AgADAQAH"

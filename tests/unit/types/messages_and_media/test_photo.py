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

from pyrogram import raw, types


def _photo(sizes: list[raw.base.PhotoSize]) -> raw.types.Photo:
    return raw.types.Photo(
        id=1,
        access_hash=2,
        file_reference=b"\x03",
        date=0,
        sizes=sizes,
        dc_id=2,
    )


def test_a_stripped_only_photo_parses_to_none() -> None:
    # `PhotoSize` is a union, so a photo whose every entry is a stripped or path constructor
    #  filters down to nothing. `photos[-1]` used to raise there:
    #  `IndexError: list index out of range`.
    photo = _photo(
        [
            raw.types.PhotoStrippedSize(
                type="i",
                bytes=b"\x01\x02",
            )
        ]
    )

    assert types.Photo._parse(None, photo) is None


def test_the_largest_concrete_size_wins_over_stripped_entries() -> None:
    photo = _photo(
        [
            raw.types.PhotoStrippedSize(
                type="i",
                bytes=b"\x01\x02",
            ),
            raw.types.PhotoSize(
                type="m",
                w=320,
                h=320,
                size=100,
            ),
            raw.types.PhotoSize(
                type="x",
                w=800,
                h=800,
                size=5000,
            ),
        ]
    )

    parsed = types.Photo._parse(None, photo)

    assert parsed is not None
    assert parsed.width == 800
    assert parsed.height == 800
    assert parsed.file_size == 5000

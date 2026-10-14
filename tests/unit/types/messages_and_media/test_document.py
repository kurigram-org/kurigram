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

import pyrogram
from pyrogram import raw, types


@pytest.mark.parametrize(
    ("thumbs", "expected"),
    [
        pytest.param(None, None, id="absent"),
        pytest.param([], None, id="empty"),
        pytest.param(
            [
                raw.types.PhotoSize(
                    type="m",
                    w=320,
                    h=320,
                    size=1,
                )
            ],
            [320],
            id="present",
        ),
    ],
)
def test_a_document_without_thumbnails_keeps_thumbs_none(
    *,
    thumbs: list[raw.base.PhotoSize] | None,
    expected: list[int] | None,
) -> None:
    # `Thumbnail._parse` returns a list, so the caller maps an empty one back to `None`.
    document = raw.types.Document(
        id=1,
        access_hash=0,
        file_reference=b"",
        date=0,
        mime_type="application/octet-stream",
        size=1,
        dc_id=1,
        attributes=[],
        thumbs=thumbs,
    )
    app = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    parsed = types.Document._parse(app, document, "file.bin")

    assert ([thumb.width for thumb in parsed.thumbs] if parsed.thumbs is not None else None) == (
        expected
    )

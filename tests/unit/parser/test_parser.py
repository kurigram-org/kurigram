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
from pyrogram.enums import ParseMode
from pyrogram.parser.parser import Parser


def _bold() -> pyrogram.raw.types.MessageEntityBold:
    return pyrogram.raw.types.MessageEntityBold(
        offset=0,
        length=4,
    )


async def test_parse_mode_default_reads_markdown() -> None:
    parsed = await Parser(None).parse("**bold**", ParseMode.DEFAULT)

    assert parsed["message"] == "bold"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(_bold())]


async def test_parse_mode_default_also_reads_html() -> None:
    parsed = await Parser(None).parse("<b>bold</b>", ParseMode.DEFAULT)

    assert parsed["message"] == "bold"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(_bold())]


async def test_parse_mode_default_is_what_no_mode_means() -> None:
    parsed = await Parser(None).parse("**bold**")

    assert parsed["message"] == "bold"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(_bold())]


async def test_parse_mode_markdown_leaves_html_alone() -> None:
    parsed = await Parser(None).parse("<b>bold</b>", ParseMode.MARKDOWN)

    assert parsed["message"] == "<b>bold</b>"
    assert parsed["entities"] is None


async def test_parse_mode_html() -> None:
    parsed = await Parser(None).parse("<b>bold</b>", ParseMode.HTML)

    assert parsed["message"] == "bold"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(_bold())]


async def test_parse_mode_html_leaves_markdown_alone() -> None:
    parsed = await Parser(None).parse("**bold**", ParseMode.HTML)

    assert parsed["message"] == "**bold**"
    assert parsed["entities"] is None


async def test_parse_mode_disabled() -> None:
    parsed = await Parser(None).parse("<b>**bold**</b>", ParseMode.DISABLED)

    assert parsed["message"] == "<b>**bold**</b>"
    assert parsed["entities"] is None


async def test_parse_rejects_an_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Invalid parse mode"):
        await Parser(None).parse("text", "markdown")  # type: ignore[arg-type]


async def test_parse_strips_the_surrounding_whitespace() -> None:
    parsed = await Parser(None).parse("  text  ", ParseMode.DISABLED)

    assert parsed["message"] == "text"


@pytest.mark.parametrize(
    ("is_html", "expected"),
    [
        pytest.param(True, "<b>bold</b>", id="html"),
        pytest.param(False, "**bold**", id="markdown"),
    ],
)
def test_unparse(
    is_html: bool,
    *,
    expected: str,
) -> None:
    entities = [
        pyrogram.types.MessageEntity(
            type=pyrogram.enums.MessageEntityType.BOLD,
            offset=0,
            length=4,
        )
    ]

    assert Parser.unparse("bold", entities, is_html) == expected

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

import pyrogram
from pyrogram import raw
from pyrogram.enums import MessageEntityType
from pyrogram.parser.entities import SPECS
from pyrogram.parser.html import HTML
from pyrogram.parser.markdown import Markdown

# One case per entity type that carries markup: the text, the entity a server would send,
#  and the raw entity `parse` has to give back after `unparse` has written it out.
#
# The expected entity is spelled out rather than taken from `MessageEntity.write()` because
#  `write()` resolves a `text_mention` through a client, which a unit test has none of.

_ROUND_TRIP_CASES: Final[tuple[pytest.ParameterSet, ...]] = (
    pytest.param(
        "bold",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.BOLD,
            offset=0,
            length=4,
        ),
        raw.types.MessageEntityBold(
            offset=0,
            length=4,
        ),
        id="bold",
    ),
    pytest.param(
        "italic",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.ITALIC,
            offset=0,
            length=6,
        ),
        raw.types.MessageEntityItalic(
            offset=0,
            length=6,
        ),
        id="italic",
    ),
    pytest.param(
        "underline",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.UNDERLINE,
            offset=0,
            length=9,
        ),
        raw.types.MessageEntityUnderline(
            offset=0,
            length=9,
        ),
        id="underline",
    ),
    pytest.param(
        "strike",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.STRIKETHROUGH,
            offset=0,
            length=6,
        ),
        raw.types.MessageEntityStrike(
            offset=0,
            length=6,
        ),
        id="strikethrough",
    ),
    pytest.param(
        "spoiler",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.SPOILER,
            offset=0,
            length=7,
        ),
        raw.types.MessageEntitySpoiler(
            offset=0,
            length=7,
        ),
        id="spoiler",
    ),
    pytest.param(
        "code",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.CODE,
            offset=0,
            length=4,
        ),
        raw.types.MessageEntityCode(
            offset=0,
            length=4,
        ),
        id="code",
    ),
    pytest.param(
        "x = 1",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.PRE,
            offset=0,
            length=5,
            language="python",
        ),
        raw.types.MessageEntityPre(
            offset=0,
            length=5,
            language="python",
        ),
        id="pre-with-language",
    ),
    pytest.param(
        "x = 1",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.PRE,
            offset=0,
            length=5,
        ),
        raw.types.MessageEntityPre(
            offset=0,
            length=5,
            language="",
        ),
        id="pre-without-language",
    ),
    pytest.param(
        "quoted",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.BLOCKQUOTE,
            offset=0,
            length=6,
        ),
        raw.types.MessageEntityBlockquote(
            offset=0,
            length=6,
            collapsed=False,
        ),
        id="blockquote",
    ),
    pytest.param(
        "quoted",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.BLOCKQUOTE,
            offset=0,
            length=6,
            expandable=True,
        ),
        raw.types.MessageEntityBlockquote(
            offset=0,
            length=6,
            collapsed=True,
        ),
        id="blockquote-expandable",
    ),
    pytest.param(
        "URL",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.TEXT_LINK,
            offset=0,
            length=3,
            url="https://pyrogram.org/",
        ),
        raw.types.MessageEntityTextUrl(
            offset=0,
            length=3,
            url="https://pyrogram.org/",
        ),
        id="text-link",
    ),
    pytest.param(
        "mention",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.TEXT_MENTION,
            offset=0,
            length=7,
            user=pyrogram.types.User(id=42),
        ),
        raw.types.InputMessageEntityMentionName(
            offset=0,
            length=7,
            user_id=42,
        ),
        id="text-mention",
    ),
    pytest.param(
        "emoji",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.CUSTOM_EMOJI,
            offset=0,
            length=5,
            custom_emoji_id=5195264424893488796,
        ),
        raw.types.MessageEntityCustomEmoji(
            offset=0,
            length=5,
            document_id=5195264424893488796,
        ),
        id="custom-emoji",
    ),
    pytest.param(
        "date",
        pyrogram.types.MessageEntity(
            type=MessageEntityType.DATE_TIME,
            offset=0,
            length=4,
            unix_time=1700000000,
            date_time_format="wD",
        ),
        raw.types.MessageEntityFormattedDate(
            offset=0,
            length=4,
            date=1700000000,
            relative=False,
            short_time=False,
            long_time=False,
            short_date=False,
            long_date=True,
            day_of_week=True,
        ),
        id="date-time",
    ),
)


@pytest.mark.parametrize(("text", "entity", "expected"), _ROUND_TRIP_CASES)
async def test_html_round_trip(
    text: str,
    *,
    entity: pyrogram.types.MessageEntity,
    expected: raw.base.MessageEntity,
) -> None:
    markup: str = HTML.unparse(
        text=text,
        entities=[entity],
    )

    parsed = await HTML(None).parse(markup)

    assert parsed["message"] == text
    # `TLObject.__eq__` compares the slots and NOT the class, so `repr` is what tells
    #  two entity types apart.
    assert [repr(each) for each in parsed["entities"]] == [repr(expected)]


@pytest.mark.parametrize(("text", "entity", "expected"), _ROUND_TRIP_CASES)
async def test_markdown_round_trip(
    text: str,
    *,
    entity: pyrogram.types.MessageEntity,
    expected: raw.base.MessageEntity,
) -> None:
    markup: str = Markdown.unparse(
        text=text,
        entities=[entity],
    )

    parsed = await Markdown(None).parse(markup)

    assert parsed["message"] == text
    assert [repr(each) for each in parsed["entities"]] == [repr(expected)]


def test_every_spec_that_writes_markup_has_a_round_trip_case() -> None:
    covered = {entity.type for _, entity, _ in (case.values for case in _ROUND_TRIP_CASES)}

    assert covered == {spec.type for spec in SPECS if spec.writes_markup}

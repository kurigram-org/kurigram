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
from pyrogram.parser.markdown import Markdown


# expected: the expected unparsed Markdown
# text: original text without entities
# entities: message entities coming from the server


def test_markdown_unparse_bold() -> None:
    expected: str = "**bold**"
    text: str = "bold"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=4
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_italic() -> None:
    expected: str = "__italic__"
    text: str = "italic"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC, offset=0, length=6
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_strike() -> None:
    expected: str = "~~strike~~"
    text: str = "strike"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.STRIKETHROUGH, offset=0, length=6
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_spoiler() -> None:
    expected: str = "||spoiler||"
    text: str = "spoiler"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER, offset=0, length=7
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_url() -> None:
    expected: str = "[URL](https://pyrogram.org/)"
    text: str = "URL"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=3,
                url="https://pyrogram.org/",
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_emoji() -> None:
    expected: str = "![🥲](tg://emoji?id=5195264424893488796) im crying"
    text: str = "🥲 im crying"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CUSTOM_EMOJI,
                offset=0,
                length=2,
                custom_emoji_id=5195264424893488796,
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_code() -> None:
    expected: str = "`code`"
    text: str = "code"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE, offset=0, length=4
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_pre() -> None:
    expected: str = """```python
for i in range(10):
    print(i)
```"""

    text: str = """for i in range(10):
    print(i)"""

    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE, offset=0, length=32, language="python"
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_blockquote() -> None:
    expected: str = """> Hello
> from

> pyrogram!"""

    text: str = """Hello\nfrom\n\npyrogram!"""

    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE, offset=0, length=10
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE, offset=12, length=9
            ),
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_mixed() -> None:
    expected: str = (
        "**aaaaaaa__aaabbb**__~~dddddddd||ddeee~~||||eeeeeeefff||ffff`fffggggggg`ggghhhhhhhhhh"
    )
    text: str = "aaaaaaaaaabbbddddddddddeeeeeeeeeeffffffffffgggggggggghhhhhhhhhh"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=13
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC, offset=7, length=6
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.STRIKETHROUGH, offset=13, length=13
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER, offset=21, length=5
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER, offset=26, length=10
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE, offset=40, length=10
            ),
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_no_entities() -> None:
    expected: str = "text"
    text: str = "text"
    entities: list[pyrogram.types.MessageEntity] = []

    assert Markdown.unparse(text=text, entities=entities) == expected


def test_markdown_unparse_html() -> None:
    expected: str = "__This works, it's ok__ <b>This shouldn't</b>"
    text: str = "This works, it's ok <b>This shouldn't</b>"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC, offset=0, length=19
            )
        ]
    )

    assert Markdown.unparse(text=text, entities=entities) == expected


# The parse side. `strict` is what `ParseMode.MARKDOWN` passes; the default is
#  `ParseMode.DEFAULT`, which also reads the HTML tags.


async def test_markdown_parse_expandable_blockquote() -> None:
    expected = pyrogram.raw.types.MessageEntityBlockquote(
        offset=0,
        length=1,
        collapsed=True,
    )

    parsed = await Markdown(None).parse("**> q||")

    assert parsed["message"] == "q"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_blockquote() -> None:
    expected = pyrogram.raw.types.MessageEntityBlockquote(
        offset=0,
        length=1,
        collapsed=False,
    )

    parsed = await Markdown(None).parse("> q")

    assert parsed["message"] == "q"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_keeps_the_line_after_a_blockquote() -> None:
    first = pyrogram.raw.types.MessageEntityBold(
        offset=0,
        length=1,
    )
    quote = pyrogram.raw.types.MessageEntityBlockquote(
        offset=2,
        length=5,
        collapsed=False,
    )
    second = pyrogram.raw.types.MessageEntityBold(
        offset=8,
        length=1,
    )

    parsed = await Markdown(None).parse("**a**\n> quote\n**b**")

    assert parsed["message"] == "a\nquote\nb"
    assert [repr(entity) for entity in parsed["entities"]] == [
        repr(first),
        repr(quote),
        repr(second),
    ]


async def test_markdown_parse_removes_a_backslash_escape() -> None:
    parsed = await Markdown(None).parse(r"\*x\*")

    assert parsed["message"] == "*x*"
    assert parsed["entities"] is None


async def test_markdown_parse_removes_a_backslash_escape_in_strict_mode() -> None:
    parsed = await Markdown(None).parse(r"\*x\*", strict=True)

    assert parsed["message"] == "*x*"
    assert parsed["entities"] is None


async def test_markdown_parse_fenced_block_swallows_no_newline() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=5,
        language="python",
    )

    parsed = await Markdown(None).parse("```python\nhello\n```")

    assert parsed["message"] == "hello"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_fence_without_a_language() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=5,
        language="",
    )

    parsed = await Markdown(None).parse("```\nplain\n```")

    assert parsed["message"] == "plain"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_keeps_an_unpaired_delimiter_as_text() -> None:
    parsed = await Markdown(None).parse("**unpaired")

    assert parsed["message"] == "**unpaired"
    assert parsed["entities"] is None


async def test_markdown_parse_does_not_read_a_delimiter_inside_code() -> None:
    expected = pyrogram.raw.types.MessageEntityCode(
        offset=0,
        length=5,
    )

    parsed = await Markdown(None).parse("`**x**`")

    assert parsed["message"] == "**x**"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_reads_html_when_not_strict() -> None:
    expected = pyrogram.raw.types.MessageEntityBold(
        offset=0,
        length=1,
    )

    parsed = await Markdown(None).parse("<b>x</b>")

    assert parsed["message"] == "x"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_link() -> None:
    expected = pyrogram.raw.types.MessageEntityTextUrl(
        offset=0,
        length=3,
        url="https://pyrogram.org/",
    )

    parsed = await Markdown(None).parse("[URL](https://pyrogram.org/)")

    assert parsed["message"] == "URL"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_crossed_entities_round_trip() -> None:
    # Crossing, not nesting: the italic starts inside the bold and ends outside it.
    entities = [
        pyrogram.types.MessageEntity(
            type=pyrogram.enums.MessageEntityType.BOLD,
            offset=0,
            length=5,
        ),
        pyrogram.types.MessageEntity(
            type=pyrogram.enums.MessageEntityType.ITALIC,
            offset=3,
            length=7,
        ),
    ]

    parsed = await Markdown(None).parse(
        Markdown.unparse(
            text="abcdefghij",
            entities=entities,
        )
    )

    assert parsed["message"] == "abcdefghij"
    assert [repr(entity) for entity in parsed["entities"]] == [
        repr(
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=5,
            )
        ),
        repr(
            pyrogram.raw.types.MessageEntityItalic(
                offset=3,
                length=7,
            )
        ),
    ]


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param("![x](tg://emoji?id=abc)", id="emoji-id-letters"),
        pytest.param("![x](tg://emoji?id=\u00b2)", id="emoji-id-superscript-digit"),
        pytest.param("![x](tg://time?unix=1&format=xyz)", id="time-format"),
        pytest.param("![x](tg://time?unix=\u00b2)", id="time-superscript-digit"),
    ],
)
async def test_markdown_parse_keeps_a_malformed_emoji_or_time_link_as_typed(markup: str) -> None:
    parsed = await Markdown(None).parse(markup)

    assert parsed["message"] == markup
    assert parsed["entities"] is None


async def test_markdown_parse_unterminated_expandable_quote_runs_to_the_end() -> None:
    expected = pyrogram.raw.types.MessageEntityBlockquote(
        offset=0,
        length=12,
        collapsed=True,
    )

    parsed = await Markdown(None).parse("**> a\nplain\nmore")

    assert parsed["message"] == "a\nplain\nmore"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_link_with_an_ampersand_in_strict_mode() -> None:
    expected = pyrogram.raw.types.MessageEntityTextUrl(
        offset=0,
        length=1,
        url="https://x.com/?a=1&b=2",
    )

    parsed = await Markdown(None).parse("[a](https://x.com/?a=1&b=2)", strict=True)

    assert parsed["message"] == "a"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_fence_language_with_a_quote_in_strict_mode() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=1,
        language='a"b',
    )

    parsed = await Markdown(None).parse('```a"b\nx\n```', strict=True)

    assert parsed["message"] == "x"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_keeps_a_backslash_before_a_letter() -> None:
    parsed = await Markdown(None).parse(r"C:\Users and \d+")

    assert parsed["message"] == r"C:\Users and \d+"
    assert parsed["entities"] is None


async def test_markdown_parse_escaped_html_tags_stay_text() -> None:
    parsed = await Markdown(None).parse(r"\<b\>x\</b\>")

    assert parsed["message"] == "<b>x</b>"
    assert parsed["entities"] is None


async def test_markdown_parse_takes_strict_positionally() -> None:
    parsed = await Markdown(None).parse("<b>x</b>", True)

    assert parsed["message"] == "<b>x</b>"
    assert parsed["entities"] is None


def test_markdown_unparse_takes_entities_positionally() -> None:
    entities: list[pyrogram.types.MessageEntity] = []

    assert Markdown.unparse("text", entities) == "text"


async def test_markdown_parse_escaped_html_characters_in_strict_mode() -> None:
    parsed = await Markdown(None).parse(r"\<\&\>", strict=True)

    assert parsed["message"] == "<&>"
    assert parsed["entities"] is None


async def test_markdown_parse_keeps_a_link_inside_code_as_text() -> None:
    expected = pyrogram.raw.types.MessageEntityCode(
        offset=0,
        length=13,
    )

    parsed = await Markdown(None).parse("`[a](http://x)`")

    assert parsed["message"] == "[a](http://x)"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_keeps_a_link_inside_a_fence_as_text() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=13,
        language="",
    )

    parsed = await Markdown(None).parse("```\n[a](http://x)\n```")

    assert parsed["message"] == "[a](http://x)"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


@pytest.mark.parametrize(
    "strict",
    [
        pytest.param(False, id="default"),
        pytest.param(True, id="strict"),
    ],
)
async def test_markdown_parse_keeps_the_backslashes_inside_code(strict: bool) -> None:
    expected = pyrogram.raw.types.MessageEntityCode(
        offset=0,
        length=11,
    )

    parsed = await Markdown(None).parse(r"`\d+\.\<b>\\`", strict=strict)

    assert parsed["message"] == r"\d+\.\<b>\\"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


@pytest.mark.parametrize(
    "strict",
    [
        pytest.param(False, id="default"),
        pytest.param(True, id="strict"),
    ],
)
async def test_markdown_parse_code_ending_in_a_backslash(strict: bool) -> None:
    expected = pyrogram.raw.types.MessageEntityCode(
        offset=0,
        length=3,
    )

    parsed = await Markdown(None).parse("`C:\\`", strict=strict)

    assert parsed["message"] == "C:\\"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_keeps_the_backslashes_inside_a_fence() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=11,
        language="python",
    )

    parsed = await Markdown(None).parse('```python\nprint("\\"")\n```')

    assert parsed["message"] == 'print("\\"")'
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_lone_backtick_keeps_the_markup_after_it() -> None:
    expected = pyrogram.raw.types.MessageEntityBold(
        offset=6,
        length=4,
    )

    parsed = await Markdown(None).parse("don`t **bold**")

    assert parsed["message"] == "don`t bold"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_keeps_a_trailing_newline_after_a_blockquote() -> None:
    expected = pyrogram.raw.types.MessageEntityBlockquote(
        offset=0,
        length=1,
        collapsed=False,
    )

    parsed = await Markdown(None).parse("> q\n")

    assert parsed["message"] == "q\n"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


def test_markdown_unparse_blockquote_ending_on_a_newline() -> None:
    # The quote covers `q\n`; a marker on the empty line after it would pull `r` in.
    entities = [
        pyrogram.types.MessageEntity(
            type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
            offset=0,
            length=2,
        ),
    ]

    assert (
        Markdown.unparse(
            text="q\nr",
            entities=entities,
        )
        == "> q\nr"
    )


def test_markdown_unparse_expandable_blockquote_ending_on_a_newline() -> None:
    # The end marker goes before the newline; after it, `||` opened the next line and the
    #  quote ran to the end of the message on the way back.
    entities = [
        pyrogram.types.MessageEntity(
            type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
            offset=0,
            length=2,
            expandable=True,
        ),
    ]

    assert (
        Markdown.unparse(
            text="q\nr",
            entities=entities,
        )
        == "**> q||\nr"
    )


async def test_markdown_parse_expandable_blockquote_right_after_a_plain_one() -> None:
    plain = pyrogram.raw.types.MessageEntityBlockquote(
        offset=0,
        length=1,
        collapsed=False,
    )
    expandable = pyrogram.raw.types.MessageEntityBlockquote(
        offset=2,
        length=1,
        collapsed=True,
    )

    parsed = await Markdown(None).parse("> a\n**> b||")

    assert parsed["message"] == "a\nb"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(plain), repr(expandable)]


async def test_markdown_parse_time_link_format_in_strict_mode() -> None:
    expected = pyrogram.raw.types.MessageEntityFormattedDate(
        offset=0,
        length=1,
        date=5,
        relative=False,
        short_time=True,
        long_time=False,
        short_date=False,
        long_date=False,
        day_of_week=False,
    )

    parsed = await Markdown(None).parse("![t](tg://time?unix=5&format=t)", strict=True)

    assert parsed["message"] == "t"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]

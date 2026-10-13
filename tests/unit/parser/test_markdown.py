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


def test_markdown_unparse_url_left_empty() -> None:
    # `MessageEntity.url` is optional, and `HTML.unparse` writes an empty `href` for it.
    expected: str = "[URL]()"
    text: str = "URL"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=3,
            )
        ]
    )

    markup: str = Markdown.unparse(
        text=text,
        entities=entities,
    )

    assert markup == expected


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


def test_markdown_unparse_marks_every_fence_line_inside_a_quote() -> None:
    expected: str = "> ```\n> a\n> b\n> ```\nc"

    text: str = "a\nb\nc"

    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=3,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE,
                offset=0,
                length=3,
                language="",
            ),
        ]
    )

    markup: str = Markdown.unparse(
        text=text,
        entities=entities,
    )

    assert markup == expected


def test_markdown_unparse_mixed() -> None:
    expected: str = (
        "**aaaaaaa__aaabbb__**~~dddddddd||ddeee||~~||eeeeeeefff||ffff`fffggggggg`ggghhhhhhhhhh"
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


def test_markdown_unparse_closes_entities_on_one_span_inner_first() -> None:
    expected: str = "**__ab__**"
    text: str = "ab"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=2,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC,
                offset=0,
                length=2,
            ),
        ]
    )

    markup: str = Markdown.unparse(
        text=text,
        entities=entities,
    )

    assert markup == expected


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


# The round-trip corpus: texts where `unparse` then `parse` must give back the
#  same text and the same entity list, because `message.text.markdown` re-sent
#  with `ParseMode.MARKDOWN` is supposed to be the identity. Parsing runs with
#  `strict=True`, which is what `ParseMode.MARKDOWN` passes; the non-strict mode
#  also reads HTML tags, so a literal `<b>` cannot round-trip there by design.
#  Passing cases stay in the table as regressions.
_UNWRITABLE_IN_FIXED_WIDTH: Final[pytest.MarkDecorator] = pytest.mark.xfail(
    strict=True,
    reason=(
        "with fixed delimiters, a backtick inside code or ``` inside pre cannot be"
        " written: no backslash escapes the closing backtick of a run"
    ),
)

_ROUND_TRIP_CORPUS: Final[tuple[pytest.ParameterSet, ...]] = (
    # Literal markdown in plain text: nothing here is an entity, so nothing may
    #  come back as one.
    pytest.param(
        "**not bold**",
        [],
        [],
        id="literal-bold-in-plain-text",
    ),
    pytest.param(
        r"a\*b",
        [],
        [],
        id="literal-backslash-in-plain-text",
    ),
    pytest.param(
        "`code`",
        [],
        [],
        id="literal-backtick-in-plain-text",
    ),
    pytest.param(
        "[click](https://example.com)",
        [],
        [],
        id="literal-link-in-plain-text",
    ),
    pytest.param(
        "> not a quote",
        [],
        [],
        id="literal-quote-marker-in-plain-text",
    ),
    pytest.param(
        "a\n> b",
        [],
        [],
        id="literal-quote-marker-on-a-later-line",
    ),
    pytest.param(
        "snake_case, 5 > 3, a-b, x|y, ~z",
        [],
        [],
        id="single-specials-stay-plain",
    ),
    pytest.param(
        "<b>not bold</b>",
        [],
        [],
        id="html-tag-stays-text-in-strict",
    ),
    # Literal markdown characters inside an entity.
    pytest.param(
        "a**b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=4,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=4,
            )
        ],
        id="stars-inside-bold",
    ),
    pytest.param(
        "__init__",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=8,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=8,
            )
        ],
        id="dunder-inside-bold",
    ),
    pytest.param(
        "a||b||c",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=7,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=7,
            )
        ],
        id="delimiter-pair-inside-bold",
    ),
    pytest.param(
        "a`b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=3,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=3,
            )
        ],
        id="backtick-inside-code",
        marks=_UNWRITABLE_IN_FIXED_WIDTH,
    ),
    pytest.param(
        r"a\*b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=4,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=4,
            )
        ],
        id="backslash-inside-code",
    ),
    pytest.param(
        "[x](y)",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=6,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=6,
            )
        ],
        id="link-syntax-inside-code",
    ),
    pytest.param(
        "a```b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE,
                offset=0,
                length=5,
                language="",
            )
        ],
        [
            pyrogram.raw.types.MessageEntityPre(
                offset=0,
                length=5,
                language="",
            )
        ],
        id="fence-inside-pre",
        marks=_UNWRITABLE_IN_FIXED_WIDTH,
    ),
    pytest.param(
        "a\n> b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE,
                offset=0,
                length=5,
                language="",
            )
        ],
        [
            pyrogram.raw.types.MessageEntityPre(
                offset=0,
                length=5,
                language="",
            )
        ],
        id="quote-marker-line-inside-pre",
    ),
    pytest.param(
        "a*",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=2,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=2,
            )
        ],
        id="star-touching-bold-close",
    ),
    pytest.param(
        "> a",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=3,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=3,
            ),
        ],
        id="quote-marker-at-the-start-of-bold",
    ),
    pytest.param(
        "a\n> b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=2,
                length=3,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=2,
                length=3,
            ),
        ],
        id="quote-marker-at-the-start-of-bold-on-a-later-line",
    ),
    pytest.param(
        r"a\-",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE,
                offset=0,
                length=3,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityUnderline(
                offset=0,
                length=3,
            ),
        ],
        id="escaped-backslash-touching-underline-close",
    ),
    pytest.param(
        "a--",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE,
                offset=0,
                length=3,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityUnderline(
                offset=0,
                length=3,
            ),
        ],
        id="run-of-dashes-touching-underline-close",
    ),
    # Nested entities.
    pytest.param(
        "bold italic",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC,
                offset=0,
                length=11,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=4,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityItalic(
                offset=0,
                length=11,
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=4,
            ),
        ],
        id="bold-inside-italic",
    ),
    pytest.param(
        "code",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=4,
                url="https://example.com/",
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=4,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=4,
                url="https://example.com/",
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=4,
            ),
        ],
        id="code-as-link-text",
    ),
    pytest.param(
        "code x",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=4,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=6,
                url="https://example.com/",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=6,
                url="https://example.com/",
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=4,
            ),
        ],
        id="code-at-the-start-of-a-longer-link",
    ),
    pytest.param(
        "x code",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=2,
                length=4,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=6,
                url="https://example.com/",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=6,
                url="https://example.com/",
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=2,
                length=4,
            ),
        ],
        id="code-at-the-end-of-a-longer-link",
    ),
    # Listed shorter first, so only the length nests them: by arrival order the bold
    #  opens outside the link and closes inside it.
    pytest.param(
        "ab",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=1,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=2,
                url="https://example.com/",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=2,
                url="https://example.com/",
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=1,
            ),
        ],
        id="bold-at-the-start-of-a-longer-link",
    ),
    pytest.param(
        "ab",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=1,
                length=1,
                url="https://example.com/",
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=2,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=2,
            ),
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=1,
                length=1,
                url="https://example.com/",
            ),
        ],
        id="link-at-the-end-of-a-longer-bold",
    ),
    pytest.param(
        "list[int]",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=9,
                url="https://example.com/",
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=9,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=9,
                url="https://example.com/",
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=9,
            ),
        ],
        id="code-with-brackets-as-link-text",
    ),
    pytest.param(
        "code",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=4,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=4,
                url="https://example.com/",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=4,
                url="https://example.com/",
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=4,
            ),
        ],
        id="code-listed-before-a-link-on-one-span",
    ),
    pytest.param(
        "code",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=4,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=4,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=4,
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=4,
            ),
        ],
        id="code-listed-before-bold-on-one-span",
    ),
    pytest.param(
        "a[ b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=2,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=3,
                length=1,
                url="https://example.com/",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=2,
            ),
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=3,
                length=1,
                url="https://example.com/",
            ),
        ],
        id="bracket-in-code-before-a-link",
    ),
    pytest.param(
        "quote",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=5,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=5,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=5,
                collapsed=False,
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=5,
            ),
        ],
        id="bold-inside-blockquote",
    ),
    pytest.param(
        "a\nb",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=3,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=3,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=3,
                collapsed=False,
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=3,
            ),
        ],
        id="bold-across-quote-lines",
    ),
    pytest.param(
        "a\nb",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=3,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=2,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=3,
                collapsed=False,
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=2,
            ),
        ],
        id="bold-closing-at-a-quote-line-start",
    ),
    pytest.param(
        "x\na\n> b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=7,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE,
                offset=2,
                length=5,
                language="",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=7,
                collapsed=False,
            ),
            pyrogram.raw.types.MessageEntityPre(
                offset=2,
                length=5,
                language="",
            ),
        ],
        id="fence-inside-a-quote",
    ),
    pytest.param(
        "a\nb\nc",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=3,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE,
                offset=0,
                length=3,
                language="",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=3,
                collapsed=False,
            ),
            pyrogram.raw.types.MessageEntityPre(
                offset=0,
                length=3,
                language="",
            ),
        ],
        id="fence-filling-a-quote",
    ),
    pytest.param(
        "q",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=1,
                expandable=True,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=1,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=1,
                collapsed=True,
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=1,
            ),
        ],
        id="bold-inside-expandable-quote",
    ),
    pytest.param(
        "q",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=1,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=1,
                expandable=True,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=1,
                collapsed=True,
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=1,
            ),
        ],
        id="bold-then-expandable-quote-on-one-span",
    ),
    pytest.param(
        "a\nq",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=3,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=2,
                length=1,
                expandable=True,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=3,
            ),
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=2,
                length=1,
                collapsed=True,
            ),
        ],
        id="bold-ending-with-an-expandable-quote",
    ),
    pytest.param(
        "a\nb",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=3,
                expandable=True,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER,
                offset=0,
                length=1,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=3,
                collapsed=True,
            ),
            pyrogram.raw.types.MessageEntitySpoiler(
                offset=0,
                length=1,
            ),
        ],
        id="spoiler-ending-a-line-of-an-expandable-quote",
    ),
    pytest.param(
        "a\nb\nc",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=5,
                expandable=True,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER,
                offset=0,
                length=3,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=5,
                collapsed=True,
            ),
            pyrogram.raw.types.MessageEntitySpoiler(
                offset=0,
                length=3,
            ),
        ],
        id="spoiler-across-lines-of-an-expandable-quote",
    ),
    pytest.param(
        "a\nb",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER,
                offset=0,
                length=3,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=2,
                length=1,
                expandable=True,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntitySpoiler(
                offset=0,
                length=3,
            ),
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=2,
                length=1,
                collapsed=True,
            ),
        ],
        id="spoiler-closing-inside-an-expandable-quote",
    ),
    pytest.param(
        "a\n\nb\nc",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=1,
                expandable=True,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=3,
                length=3,
                expandable=True,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER,
                offset=3,
                length=1,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=1,
                collapsed=True,
            ),
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=3,
                length=3,
                collapsed=True,
            ),
            pyrogram.raw.types.MessageEntitySpoiler(
                offset=3,
                length=1,
            ),
        ],
        id="spoiler-in-a-second-expandable-quote",
    ),
    # A `||` inside code is text, so it does not count toward the spoilers that decide
    #  whether the `||` after it ends the quote.
    pytest.param(
        "a||\nc",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE,
                offset=0,
                length=3,
                expandable=True,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=0,
                length=3,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBlockquote(
                offset=0,
                length=3,
                collapsed=True,
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=0,
                length=3,
            ),
        ],
        id="bars-in-code-ending-an-expandable-quote",
    ),
    pytest.param(
        "text",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=4,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC,
                offset=0,
                length=4,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=4,
            ),
            pyrogram.raw.types.MessageEntityItalic(
                offset=0,
                length=4,
            ),
        ],
        id="same-span-bold-and-italic",
    ),
    # Entities that touch.
    pytest.param(
        "ab",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=1,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=1,
                length=1,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=1,
            ),
            pyrogram.raw.types.MessageEntityBold(
                offset=1,
                length=1,
            ),
        ],
        id="adjacent-bold-runs",
    ),
    pytest.param(
        "ab",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=1,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC,
                offset=1,
                length=1,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=1,
            ),
            pyrogram.raw.types.MessageEntityItalic(
                offset=1,
                length=1,
            ),
        ],
        id="adjacent-bold-and-italic",
    ),
    pytest.param(
        "abc",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=2,
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC,
                offset=1,
                length=2,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=2,
            ),
            pyrogram.raw.types.MessageEntityItalic(
                offset=1,
                length=2,
            ),
        ],
        id="crossing-bold-and-italic",
    ),
    # Offsets: UTF-16 units, boundaries, the empty entity.
    pytest.param(
        "\U0001f600 bold",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=3,
                length=4,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=3,
                length=4,
            )
        ],
        id="bold-after-an-emoji",
    ),
    pytest.param(
        "x\U0001f600y",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=0,
                length=4,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=0,
                length=4,
            )
        ],
        id="emoji-inside-bold",
    ),
    pytest.param(
        "ab",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=1,
                length=1,
            )
        ],
        [
            pyrogram.raw.types.MessageEntityBold(
                offset=1,
                length=1,
            )
        ],
        id="bold-at-the-last-char",
    ),
    # Markdown cannot express a zero-width span, so the empty entity is dropped
    #  rather than corrupting its neighbours.
    pytest.param(
        "ab",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=1,
                length=0,
            )
        ],
        [],
        id="empty-entity-is-dropped",
    ),
    # Urls whose own characters collide with the link markup.
    pytest.param(
        "wiki",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=4,
                url="https://en.wikipedia.org/wiki/Example_(page)",
            )
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=4,
                url="https://en.wikipedia.org/wiki/Example_(page)",
            )
        ],
        id="url-with-a-closing-paren",
    ),
    pytest.param(
        "a",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=1,
                url="https://example.com/\\)",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=1,
                url="https://example.com/\\)",
            ),
        ],
        id="url-with-a-backslash-before-a-paren",
    ),
    pytest.param(
        "a\nb",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=0,
                length=3,
                url="https://example.com/",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=3,
                url="https://example.com/",
            ),
        ],
        id="link-text-across-lines",
    ),
    pytest.param(
        "x a\n> b",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=2,
                length=5,
                url="https://example.com/",
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE,
                offset=2,
                length=5,
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=2,
                length=5,
                url="https://example.com/",
            ),
            pyrogram.raw.types.MessageEntityCode(
                offset=2,
                length=5,
            ),
        ],
        id="code-across-lines-as-link-text",
    ),
    pytest.param(
        "!a",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.TEXT_LINK,
                offset=1,
                length=1,
                url="https://example.com/",
            ),
        ],
        [
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=1,
                length=1,
                url="https://example.com/",
            ),
        ],
        id="bang-before-a-link",
    ),
    pytest.param(
        "date",
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.DATE_TIME,
                offset=0,
                length=4,
                unix_time=1700000000,
                date_time_format="wD",
            )
        ],
        [
            pyrogram.raw.types.MessageEntityFormattedDate(
                offset=0,
                length=4,
                date=1700000000,
                relative=False,
                short_time=False,
                long_time=False,
                short_date=False,
                long_date=True,
                day_of_week=True,
            )
        ],
        id="date-time-format-survives-strict",
    ),
)


@pytest.mark.parametrize(("text", "entities", "expected"), _ROUND_TRIP_CORPUS)
async def test_markdown_round_trip_corpus(
    text: str,
    *,
    entities: list[pyrogram.types.MessageEntity],
    expected: list[pyrogram.raw.base.MessageEntity],
) -> None:
    markup: str = Markdown.unparse(
        text=text,
        entities=entities,
    )

    parsed = await Markdown(None).parse(markup, strict=True)

    assert parsed["message"] == text
    # `TLObject.__eq__` compares the slots and NOT the class, so `repr` is what tells
    #  two entity types apart.
    assert [repr(each) for each in (parsed["entities"] or [])] == [repr(each) for each in expected]


async def test_markdown_parse_code_run_wins_over_a_link_label() -> None:
    # CommonMark example 525: https://spec.commonmark.org/0.31.2/#example-525
    expected = pyrogram.raw.types.MessageEntityCode(
        offset=4,
        length=7,
    )

    parsed = await Markdown(None).parse("[foo`](/uri)`")

    assert parsed["message"] == "[foo](/uri)"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_escaped_bar_does_not_end_an_expandable_quote() -> None:
    expected = pyrogram.raw.types.MessageEntityBlockquote(
        offset=0,
        length=5,
        collapsed=True,
    )

    parsed = await Markdown(None).parse("**> a\\||\nc", strict=True)

    assert parsed["message"] == "a||\nc"
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


async def test_markdown_parse_keeps_a_quote_marker_inside_a_fence() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=5,
        language="",
    )

    parsed = await Markdown(None).parse("```\na\n> b\n```")

    assert parsed["message"] == "a\n> b"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_keeps_a_backslash_before_a_letter_in_a_url() -> None:
    expected = pyrogram.raw.types.MessageEntityTextUrl(
        offset=0,
        length=1,
        url="https://x.com/\\d)",
    )

    parsed = await Markdown(None).parse(r"[a](https://x.com/\d\))")

    assert parsed["message"] == "a"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_link_label_holds_a_matched_pair_of_brackets() -> None:
    expected = pyrogram.raw.types.MessageEntityTextUrl(
        offset=0,
        length=7,
        url="https://example.com/",
    )

    parsed = await Markdown(None).parse("[see [1]](https://example.com/)")

    assert parsed["message"] == "see [1]"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_markdown_parse_unmatched_bracket_ends_a_link_label() -> None:
    # As in CommonMark, an unmatched `[` cannot be link text, so the link is the
    #  innermost one; a label that read past it is what made a run of `[` quadratic.
    expected = pyrogram.raw.types.MessageEntityTextUrl(
        offset=3,
        length=1,
        url="https://example.com/",
    )

    parsed = await Markdown(None).parse("[a [b](https://example.com/)")

    assert parsed["message"] == "[a b"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]

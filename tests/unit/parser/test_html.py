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
from pyrogram.parser.html import HTML


# expected: the expected unparsed HTML
# text: original text without entities
# entities: message entities coming from the server


def test_html_unparse_bold() -> None:
    expected: str = "<b>bold</b>"
    text: str = "bold"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=4
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_italic() -> None:
    expected: str = "<i>italic</i>"
    text: str = "italic"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC, offset=0, length=6
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_underline() -> None:
    expected: str = "<u>underline</u>"
    text: str = "underline"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE, offset=0, length=9
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_strike() -> None:
    expected: str = "<s>strike</s>"
    text: str = "strike"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.STRIKETHROUGH, offset=0, length=6
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_spoiler() -> None:
    expected: str = "<tg-spoiler>spoiler</tg-spoiler>"
    text: str = "spoiler"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER, offset=0, length=7
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_url() -> None:
    expected: str = '<a href="https://pyrogram.org/">URL</a>'
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

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_code() -> None:
    expected: str = "<code>code</code>"
    text: str = "code"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE, offset=0, length=4
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_pre() -> None:
    expected: str = """<pre><code class="language-python">for i in range(10):
    print(i)</code></pre>"""

    text: str = """for i in range(10):
    print(i)"""

    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE, offset=0, length=32, language="python"
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_blockquote() -> None:
    expected: str = """<blockquote>Quote text</blockquote>
    from pyrogram"""

    text: str = """Quote text
    from pyrogram"""

    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE, offset=0, length=10
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_mixed() -> None:
    expected: str = (
        "<b>aaaaaaa<i>aaa<u>bbbb</u></i></b><u><i>bbbbbbccc</i></u><u>ccccccc<s>ddd</s></u><s>ddddd"
        "<tg-spoiler>ddeee</tg-spoiler></s><tg-spoiler>eeeeeeefff</tg-spoiler>ffff"
        "<code>fffggggggg</code>ggghhhhhhhhhh"
    )
    text: str = "aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeffffffffffgggggggggghhhhhhhhhh"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=14
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC, offset=7, length=7
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE, offset=10, length=4
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE, offset=14, length=9
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC, offset=14, length=9
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE, offset=23, length=10
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.STRIKETHROUGH, offset=30, length=3
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.STRIKETHROUGH, offset=33, length=10
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER, offset=38, length=5
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER, offset=43, length=10
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE, offset=57, length=10
            ),
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_escaped() -> None:
    expected: str = "<b>&lt;b&gt;bold&lt;/b&gt;</b>"
    text: str = "<b>bold</b>"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=11
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_escaped_nested() -> None:
    expected: str = "<b>&lt;b&gt;bold <u>&lt;u&gt;underline&lt;/u&gt;</u> bold&lt;/b&gt;</b>"
    text: str = "<b>bold <u>underline</u> bold</b>"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=33
            ),
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE, offset=8, length=16
            ),
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_no_entities() -> None:
    expected: str = "text"
    text: str = "text"
    entities: list[pyrogram.types.MessageEntity] = []

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_escapes_the_text_outside_every_entity() -> None:
    expected: str = "&lt;a&gt; <b>&lt;b&gt;</b> &lt;c&gt;"
    text: str = "<a> <b> <c>"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD,
                offset=4,
                length=3,
            )
        ]
    )

    assert (
        HTML.unparse(
            text=text,
            entities=entities,
        )
        == expected
    )


def test_html_unparse_escapes_a_message_without_entities() -> None:
    expected: str = "&lt;b&gt;"
    text: str = "<b>"
    entities: list[pyrogram.types.MessageEntity] = []

    assert (
        HTML.unparse(
            text=text,
            entities=entities,
        )
        == expected
    )


def test_html_unparse_takes_entities_positionally() -> None:
    entities: list[pyrogram.types.MessageEntity] = []

    assert HTML.unparse("text", entities) == "text"


# The parse side. `HTML.parse` needs a client only to resolve a `tg://user` mention,
#  so `None` is enough for everything below.


async def test_html_parse_spoiler() -> None:
    expected = pyrogram.raw.types.MessageEntitySpoiler(
        offset=0,
        length=1,
    )

    parsed = await HTML(None).parse('<span class="tg-spoiler">s</span>')

    assert parsed["message"] == "s"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_tg_spoiler_tag() -> None:
    expected = pyrogram.raw.types.MessageEntitySpoiler(
        offset=0,
        length=1,
    )

    parsed = await HTML(None).parse("<tg-spoiler>s</tg-spoiler>")

    assert parsed["message"] == "s"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_span_without_the_spoiler_class_is_not_an_entity() -> None:
    parsed = await HTML(None).parse('<span class="other">s</span>')

    assert parsed["message"] == '<span class="other">s</span>'
    assert parsed["entities"] is None


async def test_html_parse_plain_span_inside_a_spoiler_span_does_not_end_it() -> None:
    expected = pyrogram.raw.types.MessageEntitySpoiler(
        offset=0,
        length=16,
    )

    parsed = await HTML(None).parse('<span class="tg-spoiler">a<span>b</span>c</span>')

    assert parsed["message"] == "a<span>b</span>c"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_pre_with_language() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=3,
        language="python",
    )

    parsed = await HTML(None).parse('<pre><code class="language-python">x=1</code></pre>')

    assert parsed["message"] == "x=1"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_pre_without_language() -> None:
    expected = pyrogram.raw.types.MessageEntityPre(
        offset=0,
        length=3,
        language="",
    )

    parsed = await HTML(None).parse("<pre>x=1</pre>")

    assert parsed["message"] == "x=1"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_code_outside_a_pre_stays_code() -> None:
    expected = pyrogram.raw.types.MessageEntityCode(
        offset=0,
        length=3,
    )

    parsed = await HTML(None).parse("<code>x=1</code>")

    assert parsed["message"] == "x=1"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_unclosed_pre_keeps_its_code() -> None:
    expected = pyrogram.raw.types.MessageEntityCode(
        offset=5,
        length=3,
    )

    parsed = await HTML(None).parse('<pre><code class="language-python">x=1</code>')

    assert parsed["message"] == "<pre>x=1"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_code_covering_part_of_a_pre_is_not_its_language() -> None:
    expected = [
        pyrogram.raw.types.MessageEntityPre(
            offset=0,
            length=4,
            language="",
        ),
        pyrogram.raw.types.MessageEntityCode(
            offset=0,
            length=3,
        ),
    ]

    parsed = await HTML(None).parse('<pre><code class="language-python">x=1</code>;</pre>')

    assert parsed["message"] == "x=1;"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(entity) for entity in expected]


@pytest.mark.parametrize(
    ("markup", "language"),
    [
        pytest.param('<pre language="python"><code>x=1</code></pre>', "python", id="bare-code"),
        pytest.param('<pre><code class="other">x=1</code></pre>', "", id="class-without-language"),
        pytest.param('<pre><code class="language-">x=1</code></pre>', "", id="empty-language"),
    ],
)
async def test_html_parse_code_without_a_language_does_not_fold_into_a_pre(
    markup: str,
    language: str,
) -> None:
    expected = [
        pyrogram.raw.types.MessageEntityPre(
            offset=0,
            length=3,
            language=language,
        ),
        pyrogram.raw.types.MessageEntityCode(
            offset=0,
            length=3,
        ),
    ]

    parsed = await HTML(None).parse(markup)

    assert parsed["message"] == "x=1"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(entity) for entity in expected]


async def test_html_parse_expandable_blockquote() -> None:
    expected = pyrogram.raw.types.MessageEntityBlockquote(
        offset=0,
        length=1,
        collapsed=True,
    )

    parsed = await HTML(None).parse("<blockquote expandable>q</blockquote>")

    assert parsed["message"] == "q"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_keeps_an_unknown_tag_as_text() -> None:
    parsed = await HTML(None).parse("<marquee>x</marquee>")

    assert parsed["message"] == "<marquee>x</marquee>"
    assert parsed["entities"] is None


async def test_html_parse_keeps_an_unclosed_tag_as_text() -> None:
    parsed = await HTML(None).parse("<b>unclosed")

    assert parsed["message"] == "<b>unclosed"
    assert parsed["entities"] is None


async def test_html_parse_keeps_an_unopened_end_tag_as_text() -> None:
    parsed = await HTML(None).parse("unopened</b>")

    assert parsed["message"] == "unopened</b>"
    assert parsed["entities"] is None


async def test_html_parse_empty_markup() -> None:
    parsed = await HTML(None).parse("")

    assert parsed["message"] == ""
    assert parsed["entities"] is None


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param("x</B>", id="uppercase-end-tag"),
        pytest.param("x</b >", id="end-tag-with-a-space"),
        pytest.param("x\nyz</B>\nw</I>", id="end-tags-on-later-lines"),
        pytest.param("x</ i>", id="end-tag-read-as-a-comment"),
        pytest.param("x<![CDATA[y]]>", id="cdata"),
        pytest.param("x<!doctype html>", id="declaration"),
        pytest.param("x<?y>", id="processing-instruction"),
        pytest.param("x<br/>y", id="self-closing-tag"),
    ],
)
async def test_html_parse_keeps_markup_without_an_entity_as_typed(markup: str) -> None:
    parsed = await HTML(None).parse(markup)

    assert parsed["message"] == markup
    assert parsed["entities"] is None


async def test_html_parse_resolves_a_character_reference_once() -> None:
    expected = pyrogram.raw.types.MessageEntityBold(
        offset=0,
        length=4,
    )

    parsed = await HTML(None).parse("<b>&amp;lt;</b>")

    assert parsed["message"] == "&lt;"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_keeps_the_whitespace_inside_a_tag() -> None:
    expected = pyrogram.raw.types.MessageEntityBold(
        offset=0,
        length=3,
    )

    parsed = await HTML(None).parse("<b>\n x</b>")

    assert parsed["message"] == "\n x"
    assert [repr(entity) for entity in parsed["entities"]] == [repr(expected)]


async def test_html_parse_drops_an_empty_entity() -> None:
    parsed = await HTML(None).parse("<b></b>x")

    assert parsed["message"] == "x"
    assert parsed["entities"] is None


def test_html_unparse_crossed_entities() -> None:
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

    assert (
        HTML.unparse(
            text="abcdefghij",
            entities=entities,
        )
        == "<b>abc<i>de</b>fghij</i>"
    )


async def test_html_crossed_entities_round_trip() -> None:
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

    parsed = await HTML(None).parse(
        HTML.unparse(
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
        pytest.param('<tg-emoji emoji-id="abc">x</tg-emoji>', id="emoji-id-letters"),
        pytest.param('<tg-emoji emoji-id="\u00b2">x</tg-emoji>', id="emoji-id-superscript-digit"),
        pytest.param('<tg-time unix="1" format="xyz">x</tg-time>', id="date-time-format"),
        pytest.param('<tg-time unix="\u00b2">x</tg-time>', id="date-time-superscript-digit"),
    ],
)
async def test_html_parse_keeps_malformed_emoji_and_date_time_markup_as_text(markup: str) -> None:
    parsed = await HTML(None).parse(markup)

    assert parsed["message"] == markup
    assert parsed["entities"] is None


async def test_html_url_with_markup_characters_round_trip() -> None:
    url: str = 'https://x.com/?q="a"&amp;b'
    entities = [
        pyrogram.types.MessageEntity(
            type=pyrogram.enums.MessageEntityType.TEXT_LINK,
            offset=0,
            length=1,
            url=url,
        ),
    ]

    parsed = await HTML(None).parse(
        HTML.unparse(
            text="x",
            entities=entities,
        )
    )

    assert [repr(entity) for entity in parsed["entities"]] == [
        repr(
            pyrogram.raw.types.MessageEntityTextUrl(
                offset=0,
                length=1,
                url=url,
            )
        )
    ]


async def test_html_pre_language_with_a_quote_round_trip() -> None:
    entities = [
        pyrogram.types.MessageEntity(
            type=pyrogram.enums.MessageEntityType.PRE,
            offset=0,
            length=1,
            language='a"b',
        ),
    ]

    parsed = await HTML(None).parse(
        HTML.unparse(
            text="x",
            entities=entities,
        )
    )

    assert [repr(entity) for entity in parsed["entities"]] == [
        repr(
            pyrogram.raw.types.MessageEntityPre(
                offset=0,
                length=1,
                language='a"b',
            )
        )
    ]

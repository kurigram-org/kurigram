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
from pyrogram import raw
from pyrogram.parser.html import HTML


# expected: the expected unparsed HTML
# text: original text without entities
# entities: message entities coming from the server


def test_html_unparse_bold():
    expected = "<b>bold</b>"
    text = "bold"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=4
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_italic():
    expected = "<i>italic</i>"
    text = "italic"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.ITALIC, offset=0, length=6
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_underline():
    expected = "<u>underline</u>"
    text = "underline"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.UNDERLINE, offset=0, length=9
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_strike():
    expected = "<s>strike</s>"
    text = "strike"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.STRIKETHROUGH, offset=0, length=6
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_spoiler():
    expected = "<spoiler>spoiler</spoiler>"
    text = "spoiler"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.SPOILER, offset=0, length=7
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_url():
    expected = '<a href="https://pyrogram.org/">URL</a>'
    text = "URL"
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


def test_html_unparse_code():
    expected = "<code>code</code>"
    text = "code"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.CODE, offset=0, length=4
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_pre():
    expected = """<pre language="python">for i in range(10):
    print(i)</pre>"""

    text = """for i in range(10):
    print(i)"""

    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.PRE, offset=0, length=32, language="python"
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_blockquote():
    expected = """<blockquote>Quote text</blockquote>
    from pyrogram"""

    text = """Quote text
    from pyrogram"""

    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BLOCKQUOTE, offset=0, length=10
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_mixed():
    expected = (
        "<b>aaaaaaa<i>aaa<u>bbbb</u></i></b><u><i>bbbbbbccc</i></u><u>ccccccc<s>ddd</s></u><s>ddddd<spoiler>dd"
        "eee</spoiler></s><spoiler>eeeeeeefff</spoiler>ffff<code>fffggggggg</code>ggghhhhhhhhhh"
    )
    text = "aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeffffffffffgggggggggghhhhhhhhhh"
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


def test_html_unparse_escaped():
    expected = "<b>&lt;b&gt;bold&lt;/b&gt;</b>"
    text = "<b>bold</b>"
    entities = pyrogram.types.List(
        [
            pyrogram.types.MessageEntity(
                type=pyrogram.enums.MessageEntityType.BOLD, offset=0, length=11
            )
        ]
    )

    assert HTML.unparse(text=text, entities=entities) == expected


def test_html_unparse_escaped_nested():
    expected = "<b>&lt;b&gt;bold <u>&lt;u&gt;underline&lt;/u&gt;</u> bold&lt;/b&gt;</b>"
    text = "<b>bold <u>underline</u> bold</b>"
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


def test_html_unparse_no_entities():
    expected = "text"
    text = "text"
    entities = []

    assert HTML.unparse(text=text, entities=entities) == expected


class FakeClient:
    """Resolves every id to one fixed peer."""

    def __init__(self, peer: raw.base.InputPeer) -> None:
        self.peer = peer

    async def resolve_peer(self, peer_id: int) -> raw.base.InputPeer:
        return self.peer


_SEEN_IN = raw.types.InputPeerChannel(channel_id=5, access_hash=55)


@pytest.mark.parametrize(
    ("peer", "expected"),
    [
        (
            raw.types.InputPeerUser(user_id=42, access_hash=7),
            raw.types.InputUser(user_id=42, access_hash=7),
        ),
        # A `min` user, which `resolve_peer` addresses through a message it was seen in.
        (
            raw.types.InputPeerUserFromMessage(peer=_SEEN_IN, msg_id=3, user_id=42),
            raw.types.InputUserFromMessage(peer=_SEEN_IN, msg_id=3, user_id=42),
        ),
    ],
)
async def test_html_parse_text_mention_gets_an_input_user(
    peer: raw.base.InputPeer, expected: raw.base.InputUser
) -> None:
    parsed = await HTML(FakeClient(peer)).parse('<a href="tg://user?id=42">Dan</a>')

    (entity,) = parsed["entities"]
    # `InputMessageEntityMentionName.user_id` is an `InputUser`. Compared as bytes, since
    #  `TLObject.__eq__` looks at the fields only and would let the `InputPeer` pass.
    assert entity.user_id.write() == expected.write()

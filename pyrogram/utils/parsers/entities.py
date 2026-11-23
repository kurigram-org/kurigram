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

"""The entity table, written once.

One `EntitySpec` per message entity type carries everything the four parser halves need:
the HTML tags that open it, the Markdown delimiter that opens it, the attributes it reads
on the way in and the markup it writes on the way out. `html.py` and `markdown.py` read
this table and hold no entity table of their own.

The tags and delimiters follow the Bot API: https://core.telegram.org/bots/api#formatting-options
"""

from __future__ import annotations as _annotations

import html
import re
from dataclasses import dataclass
from typing import Final, TypeAlias

from pyrogram import raw, types
from pyrogram.enums import MessageEntityType

# The keyword arguments a generated `raw.types.MessageEntity*` constructor takes on top of
#  `offset` and `length`. A dict here is that constructor's own keyword boundary.
EntityArgumentsType: TypeAlias = dict[str, str | int | bool]

MENTION_URL: Final[str] = "tg://user?id="
CUSTOM_EMOJI_URL: Final[str] = "tg://emoji?id="
DATE_TIME_URL: Final[str] = "tg://time?unix="

BLOCKQUOTE_MARKER: Final[str] = ">"
BLOCKQUOTE_EXPANDABLE_MARKER: Final[str] = "**>"
BLOCKQUOTE_EXPANDABLE_END: Final[str] = "||"

_MENTION_URL_RE: Final[re.Pattern[str]] = re.compile(re.escape(MENTION_URL) + r"\d+")

# `r` is relative; otherwise an optional day of week, an optional date in one of two widths
#  and an optional time in one of two widths.
_DATE_TIME_FORMAT_RE: Final[re.Pattern[str]] = re.compile(r"r|w?[dD]?[tT]?")


@dataclass(frozen=True, slots=True)
class Insertion:
    """A piece of markup `unparse` inserts into the message text."""

    text: str
    offset: int


def link_url(attributes: dict[str, str]) -> str:
    """The `href` an anchor carries, empty where it carries none."""
    return attributes.get("href", "")


def valid_date_time_format(date_time_format: str) -> bool:
    return _DATE_TIME_FORMAT_RE.fullmatch(date_time_format) is not None


def date_time_flags(date_time_format: str) -> EntityArgumentsType:
    """The six `messageEntityFormattedDate` flags a format string stands for."""
    if not valid_date_time_format(date_time_format):
        raise ValueError(f"Invalid date-time format string: '{date_time_format}'")

    return {
        "relative": date_time_format == "r",
        "day_of_week": "w" in date_time_format,
        "short_date": "d" in date_time_format,
        "long_date": "D" in date_time_format,
        "short_time": "t" in date_time_format,
        "long_time": "T" in date_time_format,
    }


@dataclass(frozen=True)
class EntitySpec:
    """One entity type: the tags and the delimiter that write it, and how each is read back.

    `html_tags[0]` is the tag `unparse` writes; the rest are spellings `parse` also accepts.
    `markdown_delimiter` is empty where the Markdown shape is not a pair of delimiters, and
    the spec then overrides the two `markdown_` methods instead.
    """

    type: MessageEntityType
    html_tags: tuple[str, ...]
    markdown_delimiter: str = ""
    # Telegram detects some entities in plain text on its own. Writing markup for one of
    #  those would turn a detected entity into markup the sender never typed.
    writes_markup: bool = True

    @property
    def raw_type(self) -> type[raw.base.MessageEntity]:
        return self.type.value

    def matches(self, tag: str, *, attributes: dict[str, str]) -> bool:
        """Whether this start tag opens this entity."""
        return tag in self.html_tags

    def raw_arguments(self, attributes: dict[str, str]) -> EntityArgumentsType:
        """What the raw constructor takes beyond `offset` and `length`."""
        return {}

    def html_open(self, entity: types.MessageEntity) -> str:
        return f"<{self.html_tags[0]}>"

    def html_close(self, entity: types.MessageEntity) -> str:
        return f"</{self.html_tags[0]}>"

    def markdown_open(self, entity: types.MessageEntity) -> str:
        return self.markdown_delimiter

    def markdown_close(self, entity: types.MessageEntity) -> str:
        return self.markdown_delimiter

    def markdown_insertions(self, entity: types.MessageEntity, *, message: str) -> list[Insertion]:
        """Where this entity's Markdown goes in the message text."""
        return [
            Insertion(
                text=self.markdown_open(entity),
                offset=entity.offset,
            ),
            Insertion(
                text=self.markdown_close(entity),
                offset=entity.offset + entity.length,
            ),
        ]


@dataclass(frozen=True)
class SpoilerSpec(EntitySpec):
    def matches(self, tag: str, *, attributes: dict[str, str]) -> bool:
        if tag == "span":
            return attributes.get("class") == "tg-spoiler"

        return tag in self.html_tags


@dataclass(frozen=True)
class PreSpec(EntitySpec):
    def raw_arguments(self, attributes: dict[str, str]) -> EntityArgumentsType:
        return {"language": attributes.get("language", "")}

    def html_open(self, entity: types.MessageEntity) -> str:
        if not entity.language:
            return "<pre>"

        # Escaped as an attribute value, so that a `"` cannot end the attribute early.
        return f'<pre><code class="language-{html.escape(entity.language)}">'

    def html_close(self, entity: types.MessageEntity) -> str:
        return "</code></pre>" if entity.language else "</pre>"

    def markdown_open(self, entity: types.MessageEntity) -> str:
        return f"{self.markdown_delimiter}{entity.language or ''}\n"

    def markdown_close(self, entity: types.MessageEntity) -> str:
        return f"\n{self.markdown_delimiter}"


@dataclass(frozen=True)
class BlockquoteSpec(EntitySpec):
    def raw_arguments(self, attributes: dict[str, str]) -> EntityArgumentsType:
        return {"collapsed": "expandable" in attributes}

    def html_open(self, entity: types.MessageEntity) -> str:
        return "<blockquote expandable>" if entity.expandable else "<blockquote>"

    def markdown_insertions(self, entity: types.MessageEntity, *, message: str) -> list[Insertion]:
        end: int = entity.offset + entity.length
        lines = message[entity.offset : end].split("\n")

        # A quote that ends on a newline has an empty last line, which needs no marker.
        #  Its `||` goes before that newline: written after it, the marker opened the
        #  next line, and `parse` then ran the quote to the end of the message.
        if lines and not lines[-1]:
            lines.pop()
            end -= 1

        insertions: list[Insertion] = []
        offset: int = entity.offset

        for index, line in enumerate(lines):
            expandable: bool = bool(entity.expandable) and index == 0
            marker = BLOCKQUOTE_EXPANDABLE_MARKER if expandable else BLOCKQUOTE_MARKER

            insertions.append(
                Insertion(
                    text=f"{marker} ",
                    offset=offset,
                )
            )
            offset += len(line) + 1

        if entity.expandable:
            insertions.append(
                Insertion(
                    text=BLOCKQUOTE_EXPANDABLE_END,
                    offset=end,
                )
            )

        return insertions


@dataclass(frozen=True)
class TextLinkSpec(EntitySpec):
    def raw_arguments(self, attributes: dict[str, str]) -> EntityArgumentsType:
        return {"url": link_url(attributes)}

    def html_open(self, entity: types.MessageEntity) -> str:
        # Escaped as an attribute value: a `"` in the url ended the attribute early, and
        #  `&amp;` came back from `parse` as `&`.
        return f'<a href="{html.escape(entity.url or "")}">'

    def markdown_open(self, entity: types.MessageEntity) -> str:
        return "["

    def markdown_close(self, entity: types.MessageEntity) -> str:
        return f"]({entity.url})"


@dataclass(frozen=True)
class MentionSpec(TextLinkSpec):
    @property
    def raw_type(self) -> type[raw.base.MessageEntity]:
        # `parse` knows the user id and not the access hash, so it builds the input form
        #  `send_message` resolves; `MessageEntityMentionName` is what arrives from Telegram.
        return raw.types.InputMessageEntityMentionName

    def matches(self, tag: str, *, attributes: dict[str, str]) -> bool:
        return tag in self.html_tags and bool(_MENTION_URL_RE.fullmatch(link_url(attributes)))

    def raw_arguments(self, attributes: dict[str, str]) -> EntityArgumentsType:
        return {"user_id": int(link_url(attributes).removeprefix(MENTION_URL))}

    def html_open(self, entity: types.MessageEntity) -> str:
        return f'<a href="{MENTION_URL}{entity.user.id}">'

    def markdown_close(self, entity: types.MessageEntity) -> str:
        return f"]({MENTION_URL}{entity.user.id})"


@dataclass(frozen=True)
class EmailSpec(EntitySpec):
    def matches(self, tag: str, *, attributes: dict[str, str]) -> bool:
        return tag in self.html_tags and link_url(attributes).startswith("mailto:")


@dataclass(frozen=True)
class CustomEmojiSpec(EntitySpec):
    def matches(self, tag: str, *, attributes: dict[str, str]) -> bool:
        # Decimal, so that a malformed id keeps the tag literal instead of raising out of
        #  `int()` in `raw_arguments`. Not `isdigit()`, which also accepts `²`, and `int()`
        #  rejects that: https://docs.python.org/3.14/library/stdtypes.html#str.isdigit
        emoji_id: str = attributes.get("emoji-id") or attributes.get("id") or ""

        return tag in self.html_tags and emoji_id.isdecimal()

    def raw_arguments(self, attributes: dict[str, str]) -> EntityArgumentsType:
        return {"document_id": int(attributes.get("emoji-id") or attributes["id"])}

    def html_open(self, entity: types.MessageEntity) -> str:
        return f'<tg-emoji emoji-id="{entity.custom_emoji_id}">'

    def markdown_open(self, entity: types.MessageEntity) -> str:
        return "!["

    def markdown_close(self, entity: types.MessageEntity) -> str:
        return f"]({CUSTOM_EMOJI_URL}{entity.custom_emoji_id})"


@dataclass(frozen=True)
class DateTimeSpec(EntitySpec):
    def matches(self, tag: str, *, attributes: dict[str, str]) -> bool:
        if tag not in self.html_tags:
            return False

        # Both validated here, so that a malformed tag keeps its text instead of raising
        #  out of `raw_arguments`. `isdecimal()` for the reason `CustomEmojiSpec` gives.
        return attributes.get("unix", "").isdecimal() and valid_date_time_format(
            attributes.get("format", "")
        )

    def raw_arguments(self, attributes: dict[str, str]) -> EntityArgumentsType:
        return {
            "date": int(attributes["unix"]),
            **date_time_flags(attributes.get("format", "")),
        }

    def html_open(self, entity: types.MessageEntity) -> str:
        if not entity.date_time_format:
            return f'<tg-time unix="{entity.unix_time}">'

        return f'<tg-time unix="{entity.unix_time}" format="{entity.date_time_format}">'

    def markdown_open(self, entity: types.MessageEntity) -> str:
        return "!["

    def markdown_close(self, entity: types.MessageEntity) -> str:
        if not entity.date_time_format:
            return f"]({DATE_TIME_URL}{entity.unix_time})"

        return f"]({DATE_TIME_URL}{entity.unix_time}&format={entity.date_time_format})"


BOLD: Final[EntitySpec] = EntitySpec(
    type=MessageEntityType.BOLD,
    html_tags=("b", "strong"),
    markdown_delimiter="**",
)
ITALIC: Final[EntitySpec] = EntitySpec(
    type=MessageEntityType.ITALIC,
    html_tags=("i", "em"),
    markdown_delimiter="__",
)
UNDERLINE: Final[EntitySpec] = EntitySpec(
    type=MessageEntityType.UNDERLINE,
    html_tags=("u", "ins"),
    markdown_delimiter="--",
)
STRIKETHROUGH: Final[EntitySpec] = EntitySpec(
    type=MessageEntityType.STRIKETHROUGH,
    html_tags=("s", "del", "strike"),
    markdown_delimiter="~~",
)
SPOILER: Final[EntitySpec] = SpoilerSpec(
    type=MessageEntityType.SPOILER,
    html_tags=("tg-spoiler", "spoiler", "span"),
    markdown_delimiter="||",
)
CODE: Final[EntitySpec] = EntitySpec(
    type=MessageEntityType.CODE,
    html_tags=("code",),
    markdown_delimiter="`",
)
PRE: Final[EntitySpec] = PreSpec(
    type=MessageEntityType.PRE,
    html_tags=("pre",),
    markdown_delimiter="```",
)
BLOCKQUOTE: Final[EntitySpec] = BlockquoteSpec(
    type=MessageEntityType.BLOCKQUOTE,
    html_tags=("blockquote",),
)
MENTION: Final[EntitySpec] = MentionSpec(
    type=MessageEntityType.TEXT_MENTION,
    html_tags=("a",),
)
EMAIL: Final[EntitySpec] = EmailSpec(
    type=MessageEntityType.EMAIL,
    html_tags=("a",),
    writes_markup=False,
)
TEXT_LINK: Final[EntitySpec] = TextLinkSpec(
    type=MessageEntityType.TEXT_LINK,
    html_tags=("a",),
)
CUSTOM_EMOJI: Final[EntitySpec] = CustomEmojiSpec(
    type=MessageEntityType.CUSTOM_EMOJI,
    html_tags=("tg-emoji", "emoji"),
)
DATE_TIME: Final[EntitySpec] = DateTimeSpec(
    type=MessageEntityType.DATE_TIME,
    html_tags=("tg-time",),
)

# The three `a` specs are ordered: a mention link and a `mailto:` link are both text links
#  as far as the tag goes, so whichever reads the `href` more narrowly has to come first.
SPECS: Final[tuple[EntitySpec, ...]] = (
    BOLD,
    ITALIC,
    UNDERLINE,
    STRIKETHROUGH,
    SPOILER,
    CODE,
    PRE,
    BLOCKQUOTE,
    MENTION,
    EMAIL,
    TEXT_LINK,
    CUSTOM_EMOJI,
    DATE_TIME,
)

_SPECS_BY_TYPE: Final[dict[MessageEntityType, EntitySpec]] = {spec.type: spec for spec in SPECS}

# Longest first, so that ``` is read as a fence and not as two code delimiters. Alphabetical
#  within one length only to keep the order stable between runs.
MARKDOWN_DELIMITERS: Final[tuple[str, ...]] = tuple(
    sorted(
        {spec.markdown_delimiter for spec in SPECS if spec.markdown_delimiter},
        key=lambda delimiter: (-len(delimiter), delimiter),
    )
)

# Inside one of these, every other delimiter is literal text.
FIXED_WIDTH_DELIMITERS: Final[frozenset[str]] = frozenset(
    {CODE.markdown_delimiter, PRE.markdown_delimiter}
)

_SPECS_BY_DELIMITER: Final[dict[str, EntitySpec]] = {
    spec.markdown_delimiter: spec for spec in SPECS if spec.markdown_delimiter
}


def spec_for_tag(tag: str, *, attributes: dict[str, str]) -> EntitySpec | None:
    """The entity this start tag opens, or `None` where no entity does."""
    for spec in SPECS:
        if spec.matches(tag, attributes=attributes):
            return spec

    return None


def spec_for_type(entity_type: MessageEntityType) -> EntitySpec | None:
    """The entity's markup, or `None` for a type Telegram detects and nobody writes."""
    spec = _SPECS_BY_TYPE.get(entity_type)

    if spec is None or not spec.writes_markup:
        return None

    return spec


def spec_for_delimiter(delimiter: str) -> EntitySpec:
    """The entity a Markdown delimiter opens."""
    return _SPECS_BY_DELIMITER[delimiter]

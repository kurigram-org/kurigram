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

"""The Telegram Markdown style, read and written.

Reading rewrites the markup into the HTML style and hands it to `HTML.parse`, which owns
the offsets. Blockquotes go first, because they are decided a line at a time; the rest is
one scan for delimiters, a pass deciding which of them pair, and a rebuild. A delimiter
that pairs with nothing stays in the message as the character it is.

The delimiters themselves live in `entities.py`, once.
"""

from __future__ import annotations as _annotations

import html
import re
import string
import urllib.parse
from typing import Final

import pyrogram
from pyrogram import types
from pyrogram.enums import MessageEntityType

from . import utils
from .entities import (
    BLOCKQUOTE_EXPANDABLE_END,
    BLOCKQUOTE_EXPANDABLE_MARKER,
    BLOCKQUOTE_MARKER,
    CUSTOM_EMOJI,
    DATE_TIME,
    FIXED_WIDTH_DELIMITERS,
    MARKDOWN_DELIMITERS,
    PRE,
    TEXT_LINK,
    EntitySpec,
    Insertion,
    spec_for_delimiter,
    spec_for_type,
    valid_date_time_format,
)
from .html import HTML

_DELIMITER_PATTERN: Final[str] = "|".join(re.escape(delimiter) for delimiter in MARKDOWN_DELIMITERS)


def _markdown_re(escapable: str) -> re.Pattern[str]:
    return re.compile(
        rf"\\(?P<escaped>[{re.escape(escapable)}])"
        rf"|(?P<delimiter>{_DELIMITER_PATTERN})"
        r"|(?P<image>!?)\[(?P<label>.+?)\]\((?P<url>.+?)\)"
    )


# Only ASCII punctuation can be escaped, as in CommonMark, so that the backslashes of
#  `C:\Users` or `\d+` reach the message instead of being eaten.
#  https://spec.commonmark.org/0.31.2/#backslash-escapes
MARKDOWN_RE: Final[re.Pattern[str]] = _markdown_re(string.punctuation)

# Inside a fixed-width run no backslash escapes a backtick, so `C:\` in backticks is code
#  ending in a backslash, as in CommonMark. The other escapes are still matched there,
#  so that `_convert_inline` writes an escaped `<` as a character reference.
_FIXED_WIDTH_RE: Final[re.Pattern[str]] = _markdown_re(
    "".join(
        character
        for character in string.punctuation
        if character not in "".join(FIXED_WIDTH_DELIMITERS)
    )
)


# Splitting on the capture keeps every `\X` pair as its own odd-indexed piece.
_BACKSLASH_PAIR_RE: Final[re.Pattern[str]] = re.compile(r"(\\.)")


def _escape(line: str, *, strict: bool) -> str:
    if not strict:
        return line

    # `html.escape` must not reach inside a backslash pair: `\<` would become `\&lt;`,
    #  the escaped branch of `MARKDOWN_RE` then reads `\&` instead of `\<`, and the
    #  message carries `&lt;` where the sender typed `<`.
    pieces = _BACKSLASH_PAIR_RE.split(line)

    return "".join(piece if index % 2 else html.escape(piece) for index, piece in enumerate(pieces))


def _strip_marker(line: str, *, marker: str) -> str:
    if not line.startswith(marker):
        return line

    return line[len(marker) :].removeprefix(" ")


def _blockquote(lines: list[str], *, expandable: bool) -> str:
    attribute = " expandable" if expandable else ""

    return f"<blockquote{attribute}>{chr(10).join(lines)}</blockquote>"


def _wrap_blockquotes(text: str, *, strict: bool) -> str:
    """Every quoted run becomes one `<blockquote>`, and in strict mode the text is escaped.

    `split` rather than `splitlines`, which drops a trailing newline and shifts every offset
    after it. Escaping happens here because the markers are read before `>` becomes `&gt;`.
    """
    lines: list[str] = []
    quoted: list[str] = []
    inside: bool = False
    expandable: bool = False

    for raw_line in text.split("\n"):
        # A plain quote ends at the first line that does not carry the marker; an
        #  expandable one runs until its end marker, whatever the lines look like. The
        #  line that ends a plain quote is read afresh, since it may open the next one.
        if inside and not expandable and not raw_line.startswith(BLOCKQUOTE_MARKER):
            lines.append(_blockquote(quoted, expandable=False))

            quoted = []
            inside = False

        if inside:
            content = _strip_marker(raw_line, marker=BLOCKQUOTE_MARKER)

        elif raw_line.startswith(BLOCKQUOTE_EXPANDABLE_MARKER):
            inside = True
            expandable = True
            content = _strip_marker(raw_line, marker=BLOCKQUOTE_EXPANDABLE_MARKER)

        elif raw_line.startswith(BLOCKQUOTE_MARKER):
            inside = True
            expandable = False
            content = _strip_marker(raw_line, marker=BLOCKQUOTE_MARKER)

        else:
            lines.append(_escape(raw_line, strict=strict))
            continue

        # The opening line may carry the end marker too, which is what `**> quote||` is.
        if expandable and content.endswith(BLOCKQUOTE_EXPANDABLE_END):
            quoted.append(
                _escape(
                    content[: -len(BLOCKQUOTE_EXPANDABLE_END)],
                    strict=strict,
                )
            )
            lines.append(_blockquote(quoted, expandable=True))

            quoted = []
            inside = False
            continue

        quoted.append(_escape(content, strict=strict))

    if inside:
        lines.append(_blockquote(quoted, expandable=expandable))

    return "\n".join(lines)


def _delimiter(match: re.Match[str]) -> str | None:
    """The delimiter a match is, or `None` for an escape or a link."""
    return match.group("delimiter")


def _fixed_width_run(text: str, *, delimiter: str, position: int) -> list[re.Match[str]]:
    """The matches of a fixed-width run up to its closing delimiter, or none if none closes it."""
    run: list[re.Match[str]] = []

    for match in _FIXED_WIDTH_RE.finditer(text, position):
        run.append(match)

        if _delimiter(match) == delimiter:
            return run

    return []


def _scan(text: str) -> list[re.Match[str]]:
    """Every delimiter, link and escape, a fixed-width run read with `_FIXED_WIDTH_RE`."""
    matches: list[re.Match[str]] = []
    position: int = 0

    while (match := MARKDOWN_RE.search(text, position)) is not None:
        position = match.end()
        delimiter = _delimiter(match)

        if delimiter not in FIXED_WIDTH_DELIMITERS:
            matches.append(match)
            continue

        run = _fixed_width_run(
            text,
            delimiter=delimiter,
            position=position,
        )

        # A fixed-width delimiter that nothing closes is a literal character. Entering the
        #  run anyway turned every delimiter and link after it into text, so a lone backtick
        #  before `**x**` cost it its bold.
        if not run:
            continue

        matches.append(match)
        matches.extend(run)
        position = run[-1].end()

    return matches


def _pair(matches: list[re.Match[str]]) -> tuple[dict[int, int], set[int]]:
    """Which delimiters pair, and which links and escapes sit inside a fixed-width run.

    Anything inside a fixed-width run is left alone: a link stays text, and an escape keeps
    its backslash, since escapes do not work in code, as in CommonMark.
    https://spec.commonmark.org/0.31.2/#backslash-escapes
    `_scan` keeps only the fixed-width delimiters that open or close a run.
    """
    closes: dict[int, int] = {}
    literal: set[int] = set()
    opened: dict[str, int] = {}
    fixed_width: str | None = None

    for index, match in enumerate(matches):
        delimiter = _delimiter(match)

        if fixed_width is not None:
            if delimiter == fixed_width:
                closes[opened.pop(delimiter)] = index
                fixed_width = None

            elif delimiter is None:
                literal.add(index)

            continue

        if delimiter is None:
            continue

        if delimiter in opened:
            closes[opened.pop(delimiter)] = index
            continue

        if delimiter in FIXED_WIDTH_DELIMITERS:
            fixed_width = delimiter

        opened[delimiter] = index

    return closes, literal


def _link_markup(label: str, *, url: str, image: bool) -> str | None:
    """The HTML a `[label](url)` pair becomes, or `None` where it is not markup at all."""
    if not image:
        entity = types.MessageEntity(
            type=MessageEntityType.TEXT_LINK,
            offset=0,
            length=0,
            # `html_open` escapes the url as an attribute, and strict mode has already
            #  escaped it once.
            url=html.unescape(url),
        )

        return f"{TEXT_LINK.html_open(entity)}{label}{TEXT_LINK.html_close(entity)}"

    # The strict pass html-escapes the whole line before this one reads it, so a `&` in
    #  the query arrives as `&amp;` and `parse_qs` would read the wrong key.
    parsed = urllib.parse.urlparse(html.unescape(url))
    parameters = urllib.parse.parse_qs(parsed.query)

    # Validated before any tag is written, the way the specs' `matches` validate: a link
    #  that fails here has to survive as the text the sender typed, not as an invented
    #  literal tag.
    if parsed.netloc == "emoji":
        emoji_id: str = parameters.get("id", [""])[0]

        if not emoji_id.isdecimal():
            return None

        entity = types.MessageEntity(
            type=MessageEntityType.CUSTOM_EMOJI,
            offset=0,
            length=0,
            custom_emoji_id=emoji_id,
        )

        return f"{CUSTOM_EMOJI.html_open(entity)}{label}{CUSTOM_EMOJI.html_close(entity)}"

    if parsed.netloc == "time":
        unix_time: str = parameters.get("unix", [""])[0]
        date_time_format: str = parameters.get("format", [""])[0]

        if not unix_time.isdecimal() or not valid_date_time_format(date_time_format):
            return None

        entity = types.MessageEntity(
            type=MessageEntityType.DATE_TIME,
            offset=0,
            length=0,
            unix_time=unix_time,
            date_time_format=date_time_format,
        )

        return f"{DATE_TIME.html_open(entity)}{label}{DATE_TIME.html_close(entity)}"

    return None


def _delimiter_entity(spec: EntitySpec, *, language: str) -> types.MessageEntity:
    return types.MessageEntity(
        type=spec.type,
        offset=0,
        length=0,
        language=language,
    )


def _convert_inline(text: str) -> str:
    """Delimiters and links become HTML tags. Everything unpaired stays as it was typed."""
    matches = _scan(text)
    pairs, literal = _pair(matches)
    closings: dict[int, str] = {}

    parts: list[str] = []
    written: int = 0

    for index, match in enumerate(matches):
        if match.start() < written:
            continue

        chunk = text[written : match.start()]
        written = match.end()

        escaped = match.group("escaped")

        if escaped is not None:
            parts.append(chunk)

            if index in literal:
                parts.append("\\")

            # As a character reference, so that an escaped `<` or `&` cannot be read as
            #  markup by the HTML pass that follows.
            parts.append(f"&#{ord(escaped)};")
            continue

        delimiter = _delimiter(match)

        if delimiter is None and index in literal:
            parts.append(chunk)
            parts.append(match.group(0))
            continue

        if delimiter is None:
            markup = _link_markup(
                match.group("label"),
                url=match.group("url"),
                image=bool(match.group("image")),
            )

            parts.append(chunk)
            parts.append(match.group(0) if markup is None else markup)
            continue

        closing_tag = closings.pop(index, None)

        if closing_tag is not None:
            # A fence closes on its own line, and that newline is syntax rather than text.
            if spec_for_delimiter(delimiter) is PRE:
                chunk = chunk.removesuffix("\n")

            parts.append(chunk)
            parts.append(closing_tag)
            continue

        closing_index = pairs.get(index)

        if closing_index is None:
            parts.append(chunk)
            parts.append(delimiter)
            continue

        spec = spec_for_delimiter(delimiter)
        language: str = ""

        # An opening fence owns the rest of its line: the language, and the newline that
        #  ends it. Both are syntax, so neither reaches the message.
        if spec is PRE:
            line_end = text.find("\n", match.end())

            if line_end != -1 and line_end < matches[closing_index].start():
                # `html_open` escapes it, and strict mode has already escaped it once.
                language = html.unescape(text[match.end() : line_end])
                written = line_end + 1

        entity = _delimiter_entity(spec, language=language)
        closings[closing_index] = spec.html_close(entity)

        parts.append(chunk)
        parts.append(spec.html_open(entity))

    parts.append(text[written:])

    return "".join(parts)


class Markdown:
    def __init__(self, client: pyrogram.Client | None):
        self.html = HTML(client)

    async def parse(self, text: str, strict: bool = False) -> dict:
        return await self.html.parse(_convert_inline(_wrap_blockquotes(text, strict=strict)))

    @staticmethod
    def unparse(text: str, entities: list[types.MessageEntity]) -> str:
        text = utils.add_surrogates(text)
        insertions: list[Insertion] = []

        for entity in entities:
            spec = spec_for_type(entity.type)

            if spec is None:
                continue

            insertions.extend(spec.markdown_insertions(entity, message=text))

        parts: list[str] = []
        written: int = 0

        # A stable sort, so that two entities starting at the same offset keep the order
        #  Telegram sent them in.
        for insertion in sorted(insertions, key=lambda item: item.offset):
            parts.append(text[written : insertion.offset])
            parts.append(insertion.text)
            written = insertion.offset

        parts.append(text[written:])

        return utils.remove_surrogates("".join(parts))

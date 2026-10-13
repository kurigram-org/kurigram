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

import bisect
import html
import re
import string
import urllib.parse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

import pyrogram
from pyrogram import types
from pyrogram.enums import MessageEntityType

from . import utils
from .entities import (
    BLOCKQUOTE,
    BLOCKQUOTE_EXPANDABLE_END,
    BLOCKQUOTE_EXPANDABLE_MARKER,
    BLOCKQUOTE_MARKER,
    CODE,
    CUSTOM_EMOJI,
    DATE_TIME,
    FIXED_WIDTH_DELIMITERS,
    MARKDOWN_DELIMITERS,
    PRE,
    SPOILER,
    TEXT_LINK,
    EntitySpec,
    Insertion,
    InsertionKind,
    spec_for_delimiter,
    spec_for_type,
    valid_date_time_format,
)
from .html import HTML

if TYPE_CHECKING:
    from collections.abc import Iterable

_DELIMITER_PATTERN: Final[str] = "|".join(re.escape(delimiter) for delimiter in MARKDOWN_DELIMITERS)


# A label ends at the first unescaped `]`, a url at the first unescaped `)`; an escaped
#  pair passes through whole, so a `\]` or `\)` written by `unparse` stays inside instead
#  of closing early. A label may span lines, as the text of a link can, and holds a code
#  run whole, so `list[int]` as code in a link is not cut at its `]`. A backtick in a label
#  opens a code run when a later backtick closes it and is a lone character only when none
#  does: with a branch that also took it as plain text, a label that never closed was tried
#  in every split, so `[` before 24 code runs took 5 seconds. As in CommonMark, the code run
#  then wins over the link: https://spec.commonmark.org/0.31.2/#example-525
_LABEL_PIECE_PATTERN: Final[str] = r"\\.|`[^`]*`|`(?![^`]*`)|[^\\\[\]`]"

# A label holds a matched pair of brackets, so `[see [1]](url)` is a link, and an unmatched
#  `[` ends it, as in CommonMark: https://spec.commonmark.org/0.31.2/#link-text
#  Taking any `[` as text made every `[` of a run try the rest of the message, so 4096 of
#  them took 0.8 seconds.
_LINK_PATTERN: Final[str] = (
    rf"(?P<image>!?)\[(?P<label>(?:{_LABEL_PIECE_PATTERN}|\[(?:{_LABEL_PIECE_PATTERN})*\])+?)\]"
    r"\((?P<url>(?:\\.|[^\\)\n])+?)\)"
)


def _markdown_re(escapable: str, *, links: bool) -> re.Pattern[str]:
    pattern = rf"\\(?P<escaped>[{re.escape(escapable)}])|(?P<delimiter>{_DELIMITER_PATTERN})"

    return re.compile(f"{pattern}|{_LINK_PATTERN}" if links else pattern)


# Only ASCII punctuation can be escaped, as in CommonMark, so that the backslashes of
#  `C:\Users` or `\d+` reach the message instead of being eaten.
#  https://spec.commonmark.org/0.31.2/#backslash-escapes
MARKDOWN_RE: Final[re.Pattern[str]] = _markdown_re(
    string.punctuation,
    links=True,
)

# Inside a fixed-width run no backslash escapes a backtick, so `C:\` in backticks is code
#  ending in a backslash, as in CommonMark. The other escapes are still matched there,
#  so that `_convert_inline` writes an escaped `<` as a character reference. A link is
#  text there, and is not matched at all: a `[` in code made a label that ran past the
#  closing backtick into a later link, and the code then never closed.
_FIXED_WIDTH_RE: Final[re.Pattern[str]] = _markdown_re(
    "".join(
        character
        for character in string.punctuation
        if character not in "".join(FIXED_WIDTH_DELIMITERS)
    ),
    links=False,
)

# One escape pair, capturing the character it protects; as in `MARKDOWN_RE`, only ASCII
#  punctuation is escapable, so a url keeps the backslash of `\d`.
_ESCAPED_CHAR_RE: Final[re.Pattern[str]] = re.compile(rf"\\([{re.escape(string.punctuation)}])")

# The characters that read as a delimiter when they stand in a run: `**`, `__`, `--`,
#  `~~` and `||` are all doubled characters, so a single one is always literal text.
_PAIRABLE_CHARS: Final[str] = "*_~|-"

# What `unparse` escapes inside a text chunk: the characters that are markup on their
#  own (`\`, a backtick, `[`, `]`), and any run of a pairable character.
_CHUNK_ESCAPE_RE: Final[re.Pattern[str]] = re.compile(r"[\\`\[\]]|([*_~|-])\1+")

_QUOTE_AFTER_NEWLINE_RE: Final[re.Pattern[str]] = re.compile(r"(?<=\n)>")

# The line prefixes `_wrap_blockquotes` reads a marker after: nothing, or the `**` a
#  bold delimiter just wrote, which a following `>` would turn into `**>`.
_MARKER_PRONE_PREFIXES: Final[frozenset[str]] = frozenset({"", "**"})


def _escape_each(match: re.Match[str]) -> str:
    return "".join(f"\\{character}" for character in match.group(0))


def _escape_chunk(chunk: str, *, line_prefix: str, following: str) -> str:
    """The chunk with everything `parse` would read back as markup escaped.

    Single pairable characters stay as typed, so `snake_case` and `5 > 3` survive
    unescaped; what gets escaped is what would pair, open a link, or start a quote.
    """
    escaped = _CHUNK_ESCAPE_RE.sub(_escape_each, chunk)
    escaped = _QUOTE_AFTER_NEWLINE_RE.sub(r"\\>", escaped)

    if line_prefix in _MARKER_PRONE_PREFIXES and escaped.startswith(">"):
        escaped = f"\\{escaped}"

    # A single trailing pairable character merges with the delimiter written right
    #  after it: `a*` before a `**` close becomes `***`, and the pair then closes one
    #  character early. A run is escaped already, so the chunk decides: the escaped
    #  string can end in `\-` where an escaped backslash leaves the `-` bare.
    trailing = chunk[-1:]

    if (
        trailing
        and trailing in _PAIRABLE_CHARS
        and trailing == following[:1]
        and chunk[-2:-1] != trailing
    ):
        escaped = f"{escaped[:-1]}\\{trailing}"

    # A `!` right before the `[` of a link turns it into `![`, which `parse` reads as an
    #  emoji or a time link, and keeps as text when the url is neither.
    if following.startswith("[") and escaped.endswith("!"):
        escaped = f"{escaped[:-1]}\\!"

    return escaped


@dataclass(frozen=True, slots=True, order=True)
class _PlacedInsertion:
    """One insertion with its place in the document order.

    Offset first; at one offset the `InsertionKind` rank applies; a longer entity
    opens earlier and closes later than a shorter one, so the delimiters nest; on
    one span a fixed-width entity goes innermost, since `parse` reads everything in
    it as text and TDLib sorts code before a link or bold on the same span; and
    among equals the order Telegram sent the entities in decides, reversed for the
    closes because what opened last must close first.
    https://github.com/tdlib/td/blob/c15d3f5a5de6e3ba5839822c451152e5e18bb700/td/telegram/MessageEntity.h#L100-L110
    https://github.com/tdlib/td/blob/c15d3f5a5de6e3ba5839822c451152e5e18bb700/td/telegram/MessageEntity.cpp#L40-L66
    """

    offset: int
    rank: InsertionKind
    nesting: int
    depth: int
    arrival: int
    insertion: Insertion = field(compare=False)


def _place(
    insertion: Insertion,
    *,
    length: int,
    index: int,
    fixed_width: bool,
) -> _PlacedInsertion:
    if insertion.kind is InsertionKind.CLOSE:
        return _PlacedInsertion(
            offset=insertion.offset,
            rank=insertion.kind,
            nesting=length,
            depth=-int(fixed_width),
            arrival=-index,
            insertion=insertion,
        )

    return _PlacedInsertion(
        offset=insertion.offset,
        rank=insertion.kind,
        nesting=-length,
        depth=int(fixed_width),
        arrival=index,
        insertion=insertion,
    )


def _merged(spans: Iterable[range]) -> list[range]:
    """The spans sorted and merged, so that `_covers` can bisect them.

    Asking every span in turn, once per line or per insertion, was quadratic: 2000 code
    entities took 0.26 seconds to unparse, 100 times as long as without the check.
    """
    merged: list[range] = []

    for span in sorted(spans, key=lambda span: span.start):
        if not span:
            continue

        if merged and span.start <= merged[-1].stop:
            merged[-1] = range(merged[-1].start, max(merged[-1].stop, span.stop))
            continue

        merged.append(span)

    return merged


def _covers(position: int, *, spans: list[range]) -> bool:
    """Whether one of the spans `_merged` returned holds the position."""
    index: int = bisect.bisect_right(spans, position, key=lambda span: span.start) - 1

    return index >= 0 and position in spans[index]


def _inside(insertion: Insertion, *, spans: list[range]) -> bool:
    """Whether the insertion lands inside a span, an open at its start and a close at its end."""
    if insertion.kind is InsertionKind.OPEN:
        return _covers(insertion.offset, spans=spans)

    return _covers(insertion.offset - 1, spans=spans)


def _advance_line_prefix(prefix: str, *, piece: str) -> str:
    """What the current output line starts with, capped at what the checks compare to."""
    combined = f"{prefix}{piece}"
    newline = combined.rfind("\n")

    if newline != -1:
        combined = combined[newline + 1 :]

    return combined[:3]


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

    # A `>` line inside a fence is the fence's text, as everything in a fixed-width run is.
    fixed_width = _merged(_fixed_width_spans(text))
    line_start: int = 0

    # As in TDLib, the end marker of an expandable quote is a `||` delimiter that closes no
    #  spoiler: a spoiler ending a line of the quote writes the same `||`, and reading that
    #  as the end cut the quote short. A spoiler opened before the quote counts too, so the
    #  count runs over the whole text, less the `||` already taken as end markers.
    #  https://github.com/tdlib/td/blob/c15d3f5a5de6e3ba5839822c451152e5e18bb700/td/telegram/MessageEntity.cpp#L2285-L2300
    spoiler_ends = _spoiler_delimiter_ends(text)
    end_markers: int = 0

    for raw_line in text.split("\n"):
        start = line_start
        line_start += len(raw_line) + 1

        # A plain quote ends at the first line that does not carry the marker; an
        #  expandable one runs until its end marker, whatever the lines look like. The
        #  line that ends a plain quote is read afresh, since it may open the next one.
        if inside and not expandable and not raw_line.startswith(BLOCKQUOTE_MARKER):
            lines.append(_blockquote(quoted, expandable=False))

            quoted = []
            inside = False

        if inside:
            content = _strip_marker(raw_line, marker=BLOCKQUOTE_MARKER)

        elif _covers(start, spans=fixed_width):
            lines.append(_escape(raw_line, strict=strict))
            continue

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
            line_end: int = start + len(raw_line)
            index: int = bisect.bisect_left(spoiler_ends, line_end)
            delimiter: bool = index < len(spoiler_ends) and spoiler_ends[index] == line_end

            # A `||` that is no delimiter, as in `\||`, is text; one after an odd count of
            #  delimiters closes the spoiler they leave open.
            if not delimiter or (index - end_markers) % 2 == 1:
                quoted.append(_escape(content, strict=strict))
                continue

            end_markers += 1
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


def _spoiler_delimiter_ends(text: str) -> list[int]:
    """Where every spoiler delimiter of the text ends, in order; a `||` in code is text."""
    ends: list[int] = []
    fixed_width: str | None = None

    for match in _scan(text):
        delimiter = _delimiter(match)

        if fixed_width is not None:
            if delimiter == fixed_width:
                fixed_width = None

            continue

        if delimiter in FIXED_WIDTH_DELIMITERS:
            fixed_width = delimiter

        elif delimiter == SPOILER.markdown_delimiter:
            ends.append(match.end())

    return ends


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
    """Which delimiters pair, and which escapes sit inside a fixed-width run.

    Anything inside a fixed-width run is left alone: `_FIXED_WIDTH_RE` matches no link, and
    an escape keeps its backslash, since escapes do not work in code, as in CommonMark.
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


def _fixed_width_spans(text: str, *, offset: int = 0) -> list[range]:
    """Where the text of every closed fixed-width run lies, delimiters excluded.

    A link label is read for runs too, since `_scan` takes a link whole: code that spans
    lines in a link's text otherwise left a `>` line in it to be read as a quote.
    """
    matches = _scan(text)
    closes, _ = _pair(matches)

    spans = [
        range(offset + matches[opening].end(), offset + matches[closing].start())
        for opening, closing in closes.items()
        if _delimiter(matches[opening]) in FIXED_WIDTH_DELIMITERS
    ]

    for match in matches:
        label = match.groupdict().get("label")

        if label is not None:
            spans.extend(_fixed_width_spans(label, offset=offset + match.start("label")))

    return spans


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

        if delimiter is None:
            # The label may itself carry markup, so it goes through this same pass; the
            #  url is text, so its escape pairs just drop their backslashes.
            markup = _link_markup(
                _convert_inline(match.group("label")),
                url=_ESCAPED_CHAR_RE.sub(r"\1", match.group("url")),
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
        placed: list[_PlacedInsertion] = []

        for index, entity in enumerate(entities):
            spec = spec_for_type(entity.type)

            if spec is None:
                continue

            placed.extend(
                _place(
                    insertion,
                    length=entity.length,
                    index=index,
                    fixed_width=spec in {CODE, PRE},
                )
                for insertion in spec.markdown_insertions(entity, message=text)
            )

        # `parse` reads the text of a fixed-width run as typed, backslashes included, so
        #  an escape written there would reach the message.
        fixed_width = _merged(
            range(entity.offset, entity.offset + entity.length)
            for entity in entities
            if spec_for_type(entity.type) in {CODE, PRE}
        )

        # A fence writes line breaks the message does not have; inside a quote each one
        #  starts a line that needs the marker too, or `parse` ends the quote there and
        #  the rest of it reaches the message as a literal `<blockquote>`.
        quotes = _merged(
            range(entity.offset, entity.offset + entity.length)
            for entity in entities
            if spec_for_type(entity.type) is BLOCKQUOTE
        )

        parts: list[str] = []
        written: int = 0
        line_prefix: str = ""

        for item in sorted(placed):
            insertion = item.insertion
            chunk = text[written : insertion.offset]
            markup = insertion.text

            if "\n" in markup and _inside(insertion, spans=quotes):
                markup = markup.replace("\n", f"\n{BLOCKQUOTE_MARKER} ")

            if not _covers(written, spans=fixed_width):
                chunk = _escape_chunk(
                    chunk,
                    line_prefix=line_prefix,
                    following=markup,
                )

            parts.append(chunk)
            parts.append(markup)

            line_prefix = _advance_line_prefix(line_prefix, piece=f"{chunk}{markup}")
            written = insertion.offset

        parts.append(
            _escape_chunk(
                text[written:],
                line_prefix=line_prefix,
                following="",
            )
        )

        return utils.remove_surrogates("".join(parts))

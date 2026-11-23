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

"""The Bot API HTML style, read and written.

Reading runs in three passes: `Parser.tokenize` turns the markup into a flat list of
tokens, `_pair` decides which start tag each end tag closes, and `_build` walks the tokens
once to produce the message and its entities together. Every offset is therefore known when the entity is
constructed, and a tag that pairs with nothing survives in the message text as written.

The tags themselves live in `entities.py`, once. https://core.telegram.org/bots/api#html-style
"""

from __future__ import annotations as _annotations

import html
from dataclasses import dataclass, replace
from html.parser import HTMLParser
from typing import TypeAlias

import pyrogram
from pyrogram import raw, types
from pyrogram.errors import PeerIdInvalid

from . import utils
from .entities import EntitySpec, Insertion, InsertionKind, spec_for_tag, spec_for_type


@dataclass(frozen=True, slots=True)
class TextToken:
    """Text between tags, with its character references already resolved."""

    text: str


@dataclass(frozen=True, slots=True)
class StartToken:
    """A start tag. `spec` is `None` for a tag that opens no entity."""

    tag: str
    attributes: dict[str, str]
    source: str
    spec: EntitySpec | None


@dataclass(frozen=True, slots=True)
class EndToken:
    tag: str
    source: str


@dataclass(frozen=True, slots=True)
class MarkupToken:
    """Markup that never opens an entity, such as a comment or `<br/>`, kept as typed."""

    source: str


TokenType: TypeAlias = TextToken | StartToken | EndToken | MarkupToken


@dataclass(frozen=True, slots=True)
class ParsedMarkup:
    message: str
    entities: list[raw.base.MessageEntity]


class Parser(HTMLParser):
    """Markup in, tokens out. Nothing here knows about offsets or entities.

    Every token but text is appended with an empty `source`, which `tokenize` then cuts
    out of the markup. One parser reads one markup.
    """

    def __init__(self) -> None:
        # `convert_charrefs` resolves `&amp;` before `handle_data` sees it. Unescaping a
        #  second time there turned `&amp;lt;` into `<` instead of `&lt;`.
        super().__init__(convert_charrefs=True)

        self.tokens: list[TokenType] = []

        # Where each token starts, as `getpos()` reports it inside the handler.
        self._positions: list[tuple[int, int]] = []

    def tokenize(self, markup: str) -> list[TokenType]:
        """The tokens of `markup`, every tag carrying its source exactly as typed.

        `html.parser` hands a handler the tag name lowercased and a comment or a declaration
        without its brackets, so rebuilding the source from those turned `</B>` into `</b>`
        and `</ i>` into `<!-- i-->`. A token runs from where it starts to where the next one
        does, so the source is cut from the markup instead.
        """
        self.feed(markup)
        self.close()

        # `getpos()` counts lines from 1 and columns from 0, and only `\n` ends a line:
        #  https://github.com/python/cpython/blob/b494f5935c92951e75597bfe1c8b1f3112fec270/Lib/_markupbase.py#L32-L55
        line_starts = [
            0,
            *(index + 1 for index, character in enumerate(markup) if character == "\n"),
        ]
        starts = [line_starts[line - 1] + column for line, column in self._positions]
        ends = [*starts, len(markup)][1:]

        return [
            token if isinstance(token, TextToken) else replace(token, source=markup[start:end])
            for token, start, end in zip(self.tokens, starts, ends, strict=True)
        ]

    def _append(self, token: TokenType) -> None:
        self._positions.append(self.getpos())
        self.tokens.append(token)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # A valueless attribute such as the `expandable` of a blockquote parses as `None`.
        attributes = {name: value or "" for name, value in attrs}

        self._append(
            StartToken(
                tag=tag,
                attributes=attributes,
                source="",
                spec=spec_for_tag(tag, attributes=attributes),
            )
        )

    def handle_endtag(self, tag: str) -> None:
        self._append(
            EndToken(
                tag=tag,
                source="",
            )
        )

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag, attrs

        # No entity tag is self-closing, so `<br/>` is text and stays text.
        self._append(MarkupToken(source=""))

    def handle_data(self, data: str) -> None:
        self._append(TextToken(text=data))

    def handle_comment(self, data: str) -> None:
        del data

        self._append(MarkupToken(source=""))

    def handle_decl(self, decl: str) -> None:
        del decl

        self._append(MarkupToken(source=""))

    def handle_pi(self, data: str) -> None:
        del data

        self._append(MarkupToken(source=""))

    def unknown_decl(self, data: str) -> None:
        del data

        self._append(MarkupToken(source=""))


def _pair(tokens: list[TokenType]) -> dict[int, int]:
    """Which end token closes which start token, by index into `tokens`.

    One stack per tag name, so `<b><i>x</b></i>` still yields both entities rather than
    discarding the pair that crosses.

    A start tag that opens no entity is stacked too, so that the plain `<span>` inside
    `<span class="tg-spoiler">` takes its own `</span>` rather than ending the spoiler.
    `_build` writes both of that pair back as text.
    """
    open_by_tag: dict[str, list[int]] = {}
    pairs: dict[int, int] = {}

    for index, token in enumerate(tokens):
        if isinstance(token, StartToken):
            open_by_tag.setdefault(token.tag, []).append(index)

        elif isinstance(token, EndToken):
            opened = open_by_tag.get(token.tag)

            if opened:
                pairs[opened.pop()] = index

    return pairs


def _fold_code_into_pre(
    tokens: list[TokenType],
    *,
    pairs: dict[int, int],
) -> tuple[dict[int, str], set[int]]:
    """The language of every `pre` that a `code` pair fills exactly, and those `code` tags.

    `<pre><code class="language-python">` is one `pre` entity carrying a language, and is
    the only way the Bot API spells one. Telegram folds the two only when they cover the
    same text, so both pairs have to be adjacent: https://github.com/tdlib/td/blob/c15d3f5a5de6e3ba5839822c451152e5e18bb700/td/telegram/MessageEntity.cpp#L3600-L3617
    and only when the `code` carries a language, which only a `language-` class gives it:
    https://github.com/tdlib/td/blob/c15d3f5a5de6e3ba5839822c451152e5e18bb700/td/telegram/MessageEntity.cpp#L3513-L3515
    A bare `code` folded anyway replaced the language of `<pre language="python">`.
    Run after `_pair`, so that an unclosed `pre` keeps its `code` pair.
    """
    languages: dict[int, str] = {}
    folded: set[int] = set()

    for start, end in pairs.items():
        pre = tokens[start]
        code = tokens[start + 1]

        if not isinstance(pre, StartToken) or pre.tag != "pre":
            continue

        if (
            not isinstance(code, StartToken)
            or code.tag != "code"
            or pairs.get(start + 1) != end - 1
        ):
            continue

        code_class: str = code.attributes.get("class", "")
        language: str = code_class.removeprefix("language-")

        if language == code_class or not language:
            continue

        languages[start] = language
        folded.update((start + 1, end - 1))

    return languages, folded


def _build(tokens: list[TokenType]) -> ParsedMarkup:
    """The message text and its entities, in one left-to-right sweep."""
    pairs = _pair(tokens)
    languages, folded = _fold_code_into_pre(tokens, pairs=pairs)
    closing: dict[int, raw.base.MessageEntity] = {}

    parts: list[str] = []
    offset: int = 0
    entities: list[raw.base.MessageEntity] = []

    for index, token in enumerate(tokens):
        if index in folded:
            continue

        if isinstance(token, EndToken):
            entity = closing.pop(index, None)

            if entity is None:
                parts.append(token.source)
                offset += len(token.source)
                continue

            entity.length = offset - entity.offset
            continue

        if isinstance(token, StartToken):
            end_index = pairs.get(index)

            if end_index is None or token.spec is None:
                parts.append(token.source)
                offset += len(token.source)
                continue

            attributes = token.attributes

            if index in languages:
                attributes = {**attributes, "language": languages[index]}

            entity = token.spec.raw_type(
                offset=offset,
                length=0,
                **token.spec.raw_arguments(attributes),
            )
            closing[end_index] = entity
            entities.append(entity)
            continue

        text = token.source if isinstance(token, MarkupToken) else token.text
        parts.append(text)
        offset += len(text)

    return ParsedMarkup(
        message="".join(parts),
        entities=entities,
    )


class HTML:
    def __init__(self, client: pyrogram.Client | None):
        self.client = client

    async def parse(self, text: str) -> dict:
        parsed = _build(Parser().tokenize(utils.add_surrogates(text)))
        entities = []

        for entity in parsed.entities:
            if not entity.length:
                continue

            if isinstance(entity, raw.types.InputMessageEntityMentionName) and self.client:
                try:
                    entity.user_id = await self.client.resolve_peer(entity.user_id)

                except PeerIdInvalid:
                    continue

            entities.append(entity)

        return {
            "message": utils.remove_surrogates(parsed.message),
            "entities": sorted(entities, key=lambda entity: entity.offset) or None,
        }

    @staticmethod
    def unparse(text: str, entities: list[types.MessageEntity]) -> str:
        ordered = sorted(entities, key=lambda entity: (entity.offset, -entity.length))
        insertions: list[Insertion] = []

        def nest(entity_index: int) -> int:
            """Write one entity and every entity inside it, innermost tag last.

            Returns how many entities of `ordered` that consumed, so the caller advances
            past the whole nest without sorting the insertions afterwards.
            """
            entity = ordered[entity_index]
            spec = spec_for_type(entity.type)

            if spec is None:
                return 1

            end: int = entity.offset + entity.length

            insertions.append(
                Insertion(
                    text=spec.html_open(entity),
                    offset=entity.offset,
                    kind=InsertionKind.OPEN,
                )
            )

            inner_index: int = entity_index + 1

            while inner_index < len(ordered) and ordered[inner_index].offset < end:
                inner_index += nest(inner_index)

            insertions.append(
                Insertion(
                    text=spec.html_close(entity),
                    offset=end,
                    kind=InsertionKind.CLOSE,
                )
            )

            return inner_index - entity_index

        index: int = 0

        while index < len(ordered):
            index += nest(index)

        text = utils.add_surrogates(text)

        # `nest` appends nested runs in document order, but an entity that CROSSES another
        #  (starts inside it, ends outside) lands its closing tag out of order, and the sweep
        #  below would then re-emit the text between the two ends. A stable sort keeps the
        #  nested order at equal offsets and puts a crossing close where it belongs; the
        #  crossed tags it writes are exactly what `_pair`'s per-tag stacks read back.
        parts: list[str] = []
        written: int = 0

        for insertion in sorted(insertions, key=lambda item: item.offset):
            parts.append(html.escape(text[written : insertion.offset]))
            parts.append(insertion.text)
            written = insertion.offset

        parts.append(html.escape(text[written:]))

        return utils.remove_surrogates("".join(parts))

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

import pyrogram
from pyrogram import raw, types

from ..messages_and_media.message import Str
from ..object import Object


class TextQuote(Object):
    """Describes manually or automatically chosen quote from another message.

    Parameters:
        text (``str``):
            Text of the quoted part of a message that is replied to by the given message.
            May be empty if the quote was chosen from a rich message.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            Special entities that appear in the quote.
            Currently, only bold, italic, underline, strikethrough, spoiler, and custom_emoji entities are kept in quotes.

        rich_texts (List of :obj:`~pyrogram.types.RichText`, *optional*):
            Rich text of the quote if it was chosen from a :obj:`~pyrogram.types.RichMessage`.
            May contain only plain text, bold, italic, underline, strikethrough, spoiler, subscript,
            superscript, date and time, custom emoji, mathematical expressions, and arrays of them.

        position (``int``):
            Approximate quote position in the original message in UTF-16 code units as specified by the sender.
            For quotes from rich messages, it is the position in the text formed by joining plain texts
            of all quotable texts of the message, separated by line feeds.

        is_manual (``bool``, *optional*):
            True, if the quote was chosen manually by the message sender.
            Otherwise, the quote was added automatically by the server.

    """

    def __init__(
        self,
        *,
        text: str | None = None,
        entities: list[types.MessageEntity] | None = None,
        rich_texts: list[str | list[types.RichText] | types.RichText] | None = None,
        position: int | None = None,
        is_manual: bool | None = None,
    ):
        super().__init__()

        self.text = text
        self.entities = entities
        self.rich_texts = rich_texts
        self.position = position
        self.is_manual = is_manual

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        users: dict[int, raw.types.User],
        reply_to: raw.types.MessageReplyHeader,
    ) -> TextQuote:
        if isinstance(reply_to, raw.types.MessageReplyHeader):
            entities = types.List(
                filter(
                    lambda x: x is not None,
                    [
                        await types.MessageEntity._parse(client, entity, users)
                        for entity in reply_to.quote_entities or []
                    ],
                )
            )

            return TextQuote(
                text=Str(reply_to.quote_text).init(entities) or None,
                entities=entities or None,
                rich_texts=types.List(
                    [
                        await types.RichText._parse(client, rich_text, users)
                        for rich_text in reply_to.quote_rich or []
                    ]
                )
                or None,
                position=reply_to.quote_offset or 0,
                is_manual=reply_to.quote,
            )

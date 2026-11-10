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

from typing import TYPE_CHECKING

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import enums, types


class ReplyParameters(Object):
    """Describes reply parameters for the message that is being sent.

    Parameters:
        message_id (``int``, *optional*):
            Identifier of the message that will be replied to in the current chat, or in the chat *chat_id* if it is specified.
            Required if *ephemeral_message_id* isn't specified.

        story_id (``int``, *optional*):
            Unique identifier for the story in the chat.

        chat_id (``int`` | ``str``, *optional*):
            If the message to be replied to is from a different chat.
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages) you can simply use "me" or "self".
            For a contact that exists in your Telegram address book you can use his phone number (str).
            Not supported for messages sent on behalf of a business account and messages from channel direct messages chats.

        ephemeral_message_id (``int``, *optional*):
            Identifier of the incoming ephemeral message that will be replied to in the current chat.
            A reply to an ephemeral message must itself be an ephemeral message.
            An ephemeral message may only be replied to within 15 seconds of being sent.
            Required if *message_id* isn't specified.

        quote (``str``, *optional*):
            Quoted part of the message to be replied to, 0-1024 characters after entities parsing.
            The quote must be an exact substring of the message to be replied to, including bold, italic, underline, strikethrough, spoiler, and custom_emoji entities.
            The message will fail to send if the quote isn't found in the original message.

        quote_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        quote_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            List of special entities that appear in message text, which can be specified instead of *quote_parse_mode*.

        quote_rich_texts (List of :obj:`~pyrogram.types.RichText`, *optional*):
            List of quoted parts of the :obj:`~pyrogram.types.RichMessage` to be replied to.
            Include one element for each quoted text, in the order in which the texts appear in the message.
            A paragraph, heading, preformatted block, footer, or mathematical expression each has its own text.
            A block quotation or pull quotation has separate text and credit, and a details block has a summary.
            A table, collage, slideshow, or map has a caption, and each table cell has its own text.
            Texts in nested blocks are separate too.

            Only the first and last elements may quote a partial text. Preserve formatting and nesting.
            Quote mathematical expressions in full. Buttons, anchors and dividers can't be quoted.
            Up to 32 quoted texts with a total length of up to 1024 characters can be specified.
            Only plain text, bold, italic, underline, strikethrough, spoiler, subscript, superscript,
            date and time, custom emoji, mathematical expressions, and arrays of them are kept.
            Other rich text types are replaced with their text.
            If non-empty, then *quote*, *quote_parse_mode* and *quote_entities* are ignored.

        quote_position (``int``, *optional*):
            Position of the quote in the original message in UTF-16 code units.
            For quotes from rich messages, it is the position in the text formed by joining plain texts
            of all quotable texts of the message, separated by line feeds.

        checklist_task_id (``int``, *optional*):
            Identifier of the specific checklist task to be replied to.

        poll_option_id (``str``, *optional*):
            Persistent identifier of the specific poll option to be replied to.
    """

    def __init__(
        self,
        *,
        message_id: int | None = None,
        story_id: int | None = None,
        chat_id: int | str | None = None,
        ephemeral_message_id: int | None = None,
        quote: str | None = None,
        quote_parse_mode: enums.ParseMode | None = None,
        quote_entities: list[types.MessageEntity] | None = None,
        quote_rich_texts: list[str | list[types.RichText] | types.RichText] | None = None,
        quote_position: int | None = None,
        checklist_task_id: int | None = None,
        poll_option_id: str | None = None,
    ):
        super().__init__()

        self.message_id = message_id
        self.story_id = story_id
        self.chat_id = chat_id
        self.ephemeral_message_id = ephemeral_message_id
        self.quote = quote
        self.quote_parse_mode = quote_parse_mode
        self.quote_entities = quote_entities
        self.quote_rich_texts = quote_rich_texts
        self.quote_position = quote_position
        self.checklist_task_id = checklist_task_id
        self.poll_option_id = poll_option_id

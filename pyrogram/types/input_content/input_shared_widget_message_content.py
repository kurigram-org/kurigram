#  Kurigram - Telegram MTProto API Client Library for Python
#
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present KurimuzonAkuma <https://github.com/KurimuzonAkuma>
#
#  This file is part of Kurigram.
#
#  Kurigram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Kurigram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Kurigram. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

import pyrogram
from pyrogram import enums, raw, types, utils

from .input_message_content import InputMessageContent


class InputSharedWidgetMessageContent(InputMessageContent):
    """Represents the content of a message with a shared widget to be sent as the result of an inline query.

    .. note::
        Currently, widgets can't be sent in response to inline queries in the production environment.

    Parameters:
        widget_id (``str``):
            Unique identifier of the shared widget created by the bot.

        chat_data (``str``, *optional*):
            Data of the widget, which is specific to the message, 0-1024 bytes.

        caption (``str``, *optional*):
            Widget caption, 0-1024 characters after entities parsing.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        show_caption_above_media (``bool``, *optional*):
            Pass *True* if the caption must be shown above the widget.
    """

    def __init__(
        self,
        widget_id: str,
        chat_data: str | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
    ) -> None:
        super().__init__()

        self.widget_id = widget_id
        self.chat_data = chat_data
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.show_caption_above_media = show_caption_above_media

    async def write(
        self, client: pyrogram.Client, reply_markup: types.InlineKeyboardMarkup | None
    ) -> raw.types.InputBotInlineMessageWidgetId:
        return raw.types.InputBotInlineMessageWidgetId(
            widget_id=int(self.widget_id),
            chat_data=self.chat_data,
            invert_media=self.show_caption_above_media,
            reply_markup=await reply_markup.write(client) if reply_markup else None,
            **await utils.parse_text_entities(
                client, self.caption, self.parse_mode, self.caption_entities
            ),
        )

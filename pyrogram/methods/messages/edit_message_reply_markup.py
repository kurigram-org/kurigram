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

import pyrogram
from pyrogram import raw, types, utils

if TYPE_CHECKING:
    from datetime import datetime, timedelta


class EditMessageReplyMarkup:
    async def edit_message_reply_markup(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int,
        schedule_date: datetime | timedelta | None = None,
        reply_markup: types.InlineKeyboardMarkup | None = None,
    ) -> types.Message:
        """Edit only the reply markup of messages sent by the bot.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in chat_id.

            schedule_date (:py:obj:`~datetime.datetime` | :py:obj:`~datetime.timedelta`, *optional*):
                Date when the message will be automatically sent.
                A :py:obj:`~datetime.timedelta` is counted from now.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the edited message is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

                # Bots only
                await app.edit_message_reply_markup(
                    chat_id, message_id,
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("New button", callback_data="new_data")]]))
        """
        r = await self.invoke(
            raw.functions.messages.EditMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
            )
        )

        messages = await utils.parse_messages(
            client=self,
            messages=r,
        )

        if not messages:
            raise ValueError("The response contains no edited message")

        return messages[0]

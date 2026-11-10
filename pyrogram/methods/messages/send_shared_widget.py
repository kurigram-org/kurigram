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


class SendSharedWidget:
    async def send_shared_widget(
        self: pyrogram.Client,
        chat_id: int | str,
        widget_id: str,
        message_thread_id: int | None = None,
        chat_data: str | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        reply_markup: (
            types.InlineKeyboardMarkup
            | types.ReplyKeyboardMarkup
            | types.ReplyKeyboardRemove
            | types.ForceReply
            | None
        ) = None,
    ) -> types.Message | None:
        """Use this method to send again a shared widget created by the bot.

        .. note::
            Currently, in the production environment, widgets can be sent only to private chats,
            and sent widgets automatically have protected content and therefore can't be forwarded.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            widget_id (``str``):
                Unique identifier of the shared widget.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of a forum.
                For forum supergroups and private chats of bots with forum topic mode enabled only.

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

            disable_notification (``bool``, *optional*):
                Sends the message silently. Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            allow_paid_broadcast (``bool``, *optional*):
                Pass *True* to allow up to 1000 messages per second, ignoring
                `broadcasting limits <https://core.telegram.org/bots/faq#broadcasting-to-users>`_
                for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect to be added to the message, for private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Description of the message to reply to.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove a reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent message is returned.
        """
        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaWidgetId(widget_id=int(widget_id), chat_data=chat_data),
                invert_media=show_caption_above_media,
                silent=disable_notification,
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                effect=effect_id,
                reply_to=await utils.get_reply_to(self, reply_parameters, message_thread_id),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                random_id=self.rnd_id(),
                **await utils.parse_text_entities(self, caption, parse_mode, caption_entities),
            )
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), None)

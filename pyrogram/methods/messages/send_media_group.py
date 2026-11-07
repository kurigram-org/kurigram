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

import logging
from typing import TYPE_CHECKING

import pyrogram
from pyrogram import raw, types, utils

if TYPE_CHECKING:
    from datetime import datetime, timedelta

log = logging.getLogger(__name__)


class SendMediaGroup:
    # TODO: Add progress parameter
    async def send_media_group(
        self: pyrogram.Client,
        chat_id: int | str,
        media: list[
            types.InputMediaPhoto
            | types.InputMediaVideo
            | types.InputMediaAudio
            | types.InputMediaDocument
        ],
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | timedelta | None = None,
        protect_content: bool | None = None,
        show_caption_above_media: bool | None = None,
        business_connection_id: str | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
    ) -> list[types.Message]:
        """Send a group of photos or videos as an album.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            media (List of :obj:`~pyrogram.types.InputMediaPhoto`, :obj:`~pyrogram.types.InputMediaVideo`, :obj:`~pyrogram.types.InputMediaAudio` and :obj:`~pyrogram.types.InputMediaDocument`):
                A list describing photos and videos to be sent, must include 2–10 items.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For direct chats only.only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime` | :py:obj:`~datetime.timedelta`, *optional*):
                Date when the message will be automatically sent.
                A :py:obj:`~datetime.timedelta` is counted from now.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of the sent messages is returned.

        Raises:
            FileNotFoundError: In case a local ``os.PathLike`` doesn't point to an existing file.

        Example:
            .. code-block:: python

                from pyrogram.types import InputMediaPhoto, InputMediaVideo

                await app.send_media_group(
                    "me",
                    [
                        InputMediaPhoto("photo1.jpg"),
                        InputMediaPhoto("photo2.jpg", caption="photo caption"),
                        InputMediaVideo("video.mp4", caption="video caption")
                    ]
                )
        """
        multi_media = []

        for i in media:
            if not isinstance(
                i,
                (
                    types.InputMediaPhoto,
                    types.InputMediaVideo,
                    types.InputMediaAudio,
                    types.InputMediaDocument,
                ),
            ):
                raise ValueError(
                    f"{i.__class__.__name__} is not a supported type for send_media_group"
                )

            multi_media.append(
                raw.types.InputSingleMedia(
                    media=await i.write(client=self, chat_id=chat_id),
                    random_id=self.rnd_id(),
                    **await utils.parse_text_entities(
                        self, i.caption, i.parse_mode, i.caption_entities
                    ),
                )
            )

        r = await self.invoke(
            raw.functions.messages.SendMultiMedia(
                peer=await self.resolve_peer(chat_id),
                multi_media=multi_media,
                silent=disable_notification,
                reply_to=await utils.get_reply_to(
                    self, reply_parameters, message_thread_id, direct_messages_topic_id
                ),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                invert_media=show_caption_above_media,
                allow_paid_floodskip=allow_paid_broadcast,
                allow_paid_stars=paid_message_star_count,
                effect=effect_id,
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id,
        )

        return await utils.parse_messages(client=self, messages=r)

#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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
from pyrogram import enums, raw, types, utils

from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime


class MessageOrigin(Object):
    """This object describes the origin of a message.

    It can be one of:

    - :obj:`~pyrogram.types.MessageOriginChannel`
    - :obj:`~pyrogram.types.MessageOriginChat`
    - :obj:`~pyrogram.types.MessageOriginHiddenUser`
    - :obj:`~pyrogram.types.MessageOriginImport`
    - :obj:`~pyrogram.types.MessageOriginUser`
    """

    def __init__(self, type: enums.MessageOriginType, date: datetime | None = None):
        super().__init__()

        self.type = type
        self.date = date

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        fwd_from: raw.types.MessageFwdHeader,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> MessageOrigin:
        forward_date = utils.timestamp_to_datetime(fwd_from.date)

        if fwd_from.from_id:
            raw_peer_id = utils.get_raw_peer_id(fwd_from.from_id)
            peer_id = utils.get_peer_id(fwd_from.from_id)
            peer_type = utils.get_peer_type(peer_id)

            if peer_type == "user":
                raw_user = users.get(raw_peer_id)

                return types.MessageOriginUser(
                    date=forward_date,
                    sender_user=await types.User._parse(client, raw_user)
                    if raw_user is not None
                    else None,
                )
            else:
                raw_chat = chats.get(raw_peer_id)
                parsed_chat = (
                    await types.Chat._parse_channel_chat(client, raw_chat)
                    if raw_chat is not None
                    else None
                )

                if fwd_from.channel_post:
                    return types.MessageOriginChannel(
                        date=forward_date,
                        chat=parsed_chat,
                        message_id=fwd_from.channel_post,
                        author_signature=fwd_from.post_author,
                    )
                else:
                    return types.MessageOriginChat(
                        date=forward_date,
                        sender_chat=parsed_chat,
                        author_signature=fwd_from.post_author,
                    )

        if fwd_from.from_name:
            return types.MessageOriginHiddenUser(
                date=forward_date, sender_user_name=fwd_from.from_name
            )

        # Callers pass only a header that names its origin, so what is left is an import.
        return types.MessageOriginImport(
            date=forward_date,
            sender_user_name=fwd_from.post_author,
        )

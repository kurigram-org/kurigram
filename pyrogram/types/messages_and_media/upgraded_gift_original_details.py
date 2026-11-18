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

from pyrogram import raw, types, utils

from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime


class UpgradedGiftOriginalDetails(Object):
    """Describes the original details about the gift.

    Parameters:
        sender (:obj:`~pyrogram.types.Chat`, *optional*):
            Identifier of the user or the chat that sent the gift.

        receiver (:obj:`~pyrogram.types.Chat`, *optional*):
            Identifier of the user or the chat that received the gift.

        text (:obj:`~pyrogram.types.FormattedText`, *optional*):
            Message added to the gift.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift was sent.
    """

    def __init__(
        self,
        *,
        sender: types.Chat | None = None,
        receiver: types.Chat | None = None,
        text: types.FormattedText | None = None,
        date: datetime | None = None,
    ):
        super().__init__()

        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.date = date

    @staticmethod
    async def _parse(
        client,
        attr: raw.types.StarGiftAttributeOriginalDetails,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> UpgradedGiftOriginalDetails:
        # User and channel ids overlap, so only a user peer is looked up among the users.
        raw_sender = (
            users.get(attr.sender_id.user_id)
            if isinstance(attr.sender_id, raw.types.PeerUser)
            else None
        )
        raw_receiver = (
            users.get(attr.recipient_id.user_id)
            if isinstance(attr.recipient_id, raw.types.PeerUser)
            else None
        )

        return UpgradedGiftOriginalDetails(
            sender=await types.User._parse(client, raw_sender) if raw_sender is not None else None,
            receiver=await types.User._parse(client, raw_receiver)
            if raw_receiver is not None
            else None,
            text=await types.FormattedText._parse(client, attr.message),
            date=utils.timestamp_to_datetime(attr.date),
        )

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
from pyrogram import types
from pyrogram.errors import MessageIdInvalid


class GetMessage:
    async def get_message(
        self: pyrogram.Client,
        chat_id: int | str | None = None,
        message_id: int | str | None = None,
        replies: int = 1,
    ) -> types.Message:
        """Get one message from a chat, or fail saying which one is missing.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                Not needed when *message_id* is a link, which names the chat itself.

            message_id (``int`` | ``str``, *optional*):
                A single message identifier, or a link to the message.

            replies (``int``, *optional*):
                The number of subsequent replies to get for the message.
                Pass 0 for no reply at all or -1 for unlimited replies.
                Defaults to 1.

        Returns:
            :obj:`~pyrogram.types.Message`: The message.

        Raises:
            MessageIdInvalid: In case the message does not exist. The identifier is on the error's
                ``value``.
            ValueError: In case the arguments name no message at all, or the link cannot be read.

        Example:
            .. code-block:: python

                await app.get_message(chat_id=chat_id, message_id=12345)
                await app.get_message(message_id="https://t.me/pyrogram/49")

        The pinned message of a chat and the message a message replies to are searches rather than
        identifiers, and "there is none" is a real answer to both. Ask
        :meth:`~pyrogram.Client.get_messages` for those and read the ``None`` it gives back.
        """

        message = await self.get_messages(
            chat_id=chat_id,
            message_ids=message_id,
            replies=replies,
        )

        # `get_messages()` answers `None` for a message that does not exist, which is what a
        #  deleted one and an id nobody ever used both come back as. The caller named a single
        #  message, so there is nothing to hand back and nothing it could do with the `None`.
        if message is None:
            raise MessageIdInvalid(value=message_id)

        return message

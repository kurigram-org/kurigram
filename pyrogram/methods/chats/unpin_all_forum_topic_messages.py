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
from pyrogram import raw


class UnpinAllForumTopicMessages:
    async def unpin_all_forum_topic_messages(
        self: pyrogram.Client, chat_id: int | str, message_thread_id: int
    ) -> bool:
        """Use this method to clear the list of pinned messages in a forum topic in a forum supergroup chat or a private chat with a user.
        In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the `can_pin_messages` administrator right in the supergroup.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_thread_id (``int``):
                Unique identifier for the target message thread of the forum topic.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Unpin all forum topic messages
                await app.unpin_all_forum_topic_messages(chat_id, message_thread_id)
        """
        r = await self.invoke(
            raw.functions.messages.UnpinAllMessages(
                peer=await self.resolve_peer(chat_id), top_msg_id=message_thread_id
            )
        )

        return bool(r)


class UnpinAllGeneralForumTopicMessages:
    async def unpin_all_general_forum_topic_messages(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> bool:
        """Use this method to clear the list of pinned messages in a General forum topic.
        In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the `can_pin_messages` administrator right in the supergroup.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Unpin all forum topic messages
                await app.unpin_all_general_forum_topic_messages(chat_id)
        """
        return bool(await self.unpin_all_forum_topic_messages(chat_id, message_thread_id=1))

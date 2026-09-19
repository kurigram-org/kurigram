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


class CreateForumTopic:
    async def create_forum_topic(
        self: pyrogram.Client,
        chat_id: int | str,
        name: str,
        icon_color: int | None = None,
        icon_custom_emoji_id: str | None = None,
    ) -> types.ForumTopic:
        """Use this method to create a topic in a forum supergroup chat or a private chat with a user.
        In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the `can_manage_topics` administrator right.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            name (``str``):
                Topic name, 1-128 characters.

            icon_color (``int``, *optional*):
                Color of the topic icon in RGB format.
                Currently, must be one of 7322096 (0x6FB9F0), 16766590 (0xFFD67E), 13338331 (0xCB86DB), 9367192 (0x8EEE98), 16749490 (0xFF93B2), or 16478047 (0xFB6F5F).

            icon_custom_emoji_id (``str``, *optional*):
                Unique identifier of the custom emoji shown as the topic icon.

        Returns:
            :obj:`~pyrogram.types.ForumTopic`: On success, information about the created topic is returned.

        Example:
            .. code-block:: python

                await app.create_forum_topic(chat_id=chat_id, name="Topic Name")
        """
        r = await self.invoke(
            raw.functions.messages.CreateForumTopic(
                peer=await self.resolve_peer(chat_id),
                title=name,
                random_id=self.rnd_id(),
                icon_color=icon_color,
                icon_emoji_id=int(icon_custom_emoji_id)
                if icon_custom_emoji_id is not None
                else None,
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        return await types.ForumTopic._parse_message(
            client=self, message=r.updates[1].message, users=users, chats=chats
        )

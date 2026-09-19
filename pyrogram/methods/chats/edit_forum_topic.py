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


class EditForumTopic:
    async def edit_forum_topic(
        self: pyrogram.Client,
        chat_id: int | str,
        message_thread_id: int,
        name: str | None = None,
        icon_custom_emoji_id: str | None = None,
    ) -> bool:
        """Use this method to edit name and icon of a topic in a forum supergroup chat or a private chat with a user.
        In the case of a supergroup chat the bot must be an administrator in the chat for this to work and must have the `can_manage_topics` administrator rights, unless it is the creator of the topic.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_thread_id (``int``):
                Unique identifier for the target message thread of the forum topic.

            name (``str``, *optional*):
                New topic name, 0-128 characters.
                If not specified or empty, the current name of the topic will be kept.

            icon_custom_emoji_id (``str``, *optional*):
                New unique identifier of the custom emoji shown as the topic icon.
                Pass an empty string to remove the icon.
                If not specified, the current icon will be kept.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_forum_topic(chat_id, message_thread_id, "New Topic Title")
        """
        if icon_custom_emoji_id == "":
            icon_emoji_id = 0
        else:
            icon_emoji_id = int(icon_custom_emoji_id) if icon_custom_emoji_id is not None else None

        r = await self.invoke(
            raw.functions.messages.EditForumTopic(
                peer=await self.resolve_peer(chat_id),
                topic_id=message_thread_id,
                title=name,
                icon_emoji_id=icon_emoji_id,
            )
        )

        return bool(r)


class EditGeneralForumTopic:
    async def edit_general_forum_topic(
        self: pyrogram.Client,
        chat_id: int | str,
        name: str,
    ) -> bool:
        """Use this method to edit the name of the 'General' topic in a forum supergroup chat.
        The bot must be an administrator in the chat for this to work and must have the `can_manage_topics` administrator rights.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            name (``str``):
                New topic name, 1-128 characters.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_general_forum_topic(chat_id, "New Topic Title")
        """
        return bool(await self.edit_forum_topic(chat_id, 1, name=name))

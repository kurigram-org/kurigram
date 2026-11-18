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
from pyrogram import errors, raw


class ToggleForumTopics:
    async def toggle_forum_topics(
        self: pyrogram.Client,
        chat_id: int | str,
        is_forum: bool = False,
        has_forum_tabs: bool = False,
        has_forum_sidebar: bool = False,
    ) -> bool:
        """Enable or disable forum functionality in a supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            is_forum (``bool``, *optional*):
                The new status.
                Pass True to enable forum topics.
                Defaults to False.

            has_forum_tabs (``bool``, *optional*):
                Whether to enable or disable tabs in the forum.
                Ignored if is_forum is False.
                Defaults to False.

            has_forum_sidebar (``bool``, *optional*):
                Whether to enable or disable sidebar in the forum.
                Ignored if is_forum is False.
                Must be False if has_forum_tabs is True.
                Defaults to False.

        Returns:
            ``bool``: True on success. False otherwise.

        Example:
            .. code-block:: python

                # Change status of topics to disabled
                await app.toggle_forum_topics(is_forum=False)

                # Change status of topics to enabled
                await app.toggle_forum_topics(is_forum=True)
        """
        try:
            r = await self.invoke(
                raw.functions.channels.ToggleForum(
                    channel=await self.resolve_peer(chat_id),
                    enabled=is_forum,
                    tabs=has_forum_tabs,
                    sidebar=has_forum_sidebar,
                )
            )

            return bool(r)
        except errors.RPCError:
            return False

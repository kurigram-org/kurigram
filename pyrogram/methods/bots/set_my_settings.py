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


class SetMySettings:
    async def set_my_settings(
        self: pyrogram.Client,
        *,
        supports_inline_queries: bool | None = None,
        inline_query_placeholder: str | None = None,
        needs_inline_query_location: bool | None = None,
        inline_feedback_share_denominator: int | None = None,
        can_join_groups: bool | None = None,
        can_read_all_group_messages: bool | None = None,
        can_connect_to_business: bool | None = None,
        can_manage_bots: bool | None = None,
        supports_guest_queries: bool | None = None,
        supports_join_request_queries: bool | None = None,
        has_topics_enabled: bool | None = None,
        allows_users_to_create_topics: bool | None = None,
        has_topic_sidebar: bool | None = None,
        can_communicate_with_bots: bool | None = None,
        callback_query_mode: str | None = None,
        for_my_bot: int | str | None = None,
    ) -> bool:
        """Change the settings of a bot. Settings that aren't specified remain unchanged.

        .. note::

            If the current account is an User, can be called only if the ``for_my_bot`` has ``can_be_edited`` property set to True.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            supports_inline_queries (``bool``, *optional*):
                Pass True to enable inline mode, False to disable it.

            inline_query_placeholder (``str``, *optional*):
                New placeholder for inline queries. Pass an empty string to restore the default.

            needs_inline_query_location (``bool``, *optional*):
                Pass True to request the user's location with every inline query.

            inline_feedback_share_denominator (``int``, *optional*):
                Share of chosen inline results to receive: 1, 10, 100 or 1000. Pass 0 to stop receiving them.

            can_join_groups (``bool``, *optional*):
                Pass True to allow adding the bot to groups.

            can_read_all_group_messages (``bool``, *optional*):
                Pass True to disable privacy mode, False to enable it.

            can_connect_to_business (``bool``, *optional*):
                Pass True to allow connecting the bot to user accounts.

            can_manage_bots (``bool``, *optional*):
                Pass True to allow creating other bots controlled by this bot.

            supports_guest_queries (``bool``, *optional*):
                Pass True to allow guest queries from chats the bot isn't in.

            supports_join_request_queries (``bool``, *optional*):
                Pass True to allow assigning the bot to process join request queries.

            has_topics_enabled (``bool``, *optional*):
                Pass True to enable forum topic mode in private chats with the bot.

            allows_users_to_create_topics (``bool``, *optional*):
                Pass True to allow users to create and delete topics in private chats.

            has_topic_sidebar (``bool``, *optional*):
                Pass True to show topics in private chats in a sidebar.

            can_communicate_with_bots (``bool``, *optional*):
                Pass True to allow communication with other bots.

            callback_query_mode (``str``, *optional*):
                How callback queries from bot-sent messages are received: "default", "auto" or "inline".

            for_my_bot (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the bot whose settings are changed, instead of the current user's.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_my_settings(can_join_groups=False, callback_query_mode="auto")
        """
        # The server spells the default mode as an empty string, and stores "can join" as "no chats"
        await self.invoke(
            raw.functions.bots.SetBotSettings(
                bot=await self.resolve_peer(for_my_bot) if for_my_bot else None,
                inline_mode=supports_inline_queries,
                inline_placeholder=inline_query_placeholder,
                inline_geo=needs_inline_query_location,
                inline_feedback=inline_feedback_share_denominator,
                nochats=None if can_join_groups is None else not can_join_groups,
                chat_history=can_read_all_group_messages,
                business=can_connect_to_business,
                can_manage_bots=can_manage_bots,
                guestchat=supports_guest_queries,
                guard=supports_join_request_queries,
                forum_view=has_topics_enabled,
                forum_can_manage_topics=allows_users_to_create_topics,
                forum_sidebar=has_topic_sidebar,
                bot_to_bot_communication_mode=can_communicate_with_bots,
                callback_mode="" if callback_query_mode == "default" else callback_query_mode,
            )
        )

        return True

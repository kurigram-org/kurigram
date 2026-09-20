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

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object

if TYPE_CHECKING:
    from datetime import datetime


class ForumTopic(Object):
    """A forum topic.

    Parameters:
        id (``int``):
            Unique topic identifier inside this chat.

        name (``str``):
            The topic title.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the topic was created.

        icon_color (``int``, *optional*):
            Color of the topic icon in RGB format.

        icon_custom_emoji_id (``str``, *optional*):
            Unique identifier of the custom emoji shown as the topic icon.

        creator (:obj:`~pyrogram.types.Chat`, *optional*):
            Topic creator.

        top_message (:obj:`~pyrogram.types.Message`, *optional*):
            The last message sent in the topic at this time.

        unread_count (``int``, *optional*):
            Amount of unread messages in this topic.

        unread_mentions_count (``int``, *optional*):
            Amount of unread messages containing a mention in this topic.

        unread_reactions_count (``int``, *optional*):
            Amount of unread messages containing a reaction in this topic.

        unread_poll_vote_count (``int``, *optional*):
            Number of messages with unread poll votes in the topic.

        is_my (``bool``, *optional*):
            True, if the topic was created by the current user.

        is_closed (``bool``, *optional*):
            True, the topic is closed (no messages can be sent to it).

        is_pinned (``bool``, *optional*):
            True, if the topic is pinned.

        is_short (``bool``, *optional*):
            True, if the topic is a reduced version of the full topic information.

            If set, only the ``is_my``, ``is_closed``, ``id``, ``date``, ``title``, ``icon_color``, ``icon_emoji_id`` and ``creator`` parameters will contain valid information.

        is_hidden (``bool``, *optional*):
            True, if the topic is hidden (only valid for the "General" topic, ``id=1``).

        is_deleted (``bool``, *optional*):
            True, if the forum topic is deleted.
    """

    def __init__(
        self,
        *,
        id: int,
        name: str | None = None,
        date: datetime | None = None,
        icon_color: int | None = None,
        icon_custom_emoji_id: str | None = None,
        creator: types.Chat | None = None,
        top_message: types.Message | None = None,
        unread_count: int | None = None,
        unread_mentions_count: int | None = None,
        unread_reactions_count: int | None = None,
        unread_poll_vote_count: int | None = None,
        is_my: bool | None = None,
        is_closed: bool | None = None,
        is_pinned: bool | None = None,
        is_short: bool | None = None,
        is_hidden: bool | None = None,
        is_deleted: bool | None = None,
    ):
        super().__init__()

        self.id = id
        self.name = name
        self.date = date
        self.icon_color = icon_color
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.creator = creator
        self.top_message = top_message
        self.unread_count = unread_count
        self.unread_mentions_count = unread_mentions_count
        self.unread_reactions_count = unread_reactions_count
        self.unread_poll_vote_count = unread_poll_vote_count
        self.is_my = is_my
        self.is_closed = is_closed
        self.is_pinned = is_pinned
        self.is_short = is_short
        self.is_hidden = is_hidden
        self.is_deleted = is_deleted

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        forum_topic: raw.base.ForumTopic,
        messages: dict | None = None,
        users: dict | None = None,
        chats: dict | None = None,
    ) -> ForumTopic | None:
        if not forum_topic:
            return None

        if isinstance(forum_topic, raw.types.ForumTopicDeleted):
            return ForumTopic(id=forum_topic.id, is_deleted=True)

        messages = messages or {}
        users = users or {}
        chats = chats or {}

        peer_id = utils.get_raw_peer_id(forum_topic.from_id)

        return ForumTopic(
            id=forum_topic.id,
            name=forum_topic.title,
            date=utils.timestamp_to_datetime(forum_topic.date),
            icon_color=forum_topic.icon_color,
            icon_custom_emoji_id=str(forum_topic.icon_emoji_id),
            creator=await types.Chat._parse_chat(client, users.get(peer_id) or chats.get(peer_id)),
            top_message=messages.get(forum_topic.top_message),
            unread_count=forum_topic.unread_count,
            unread_mentions_count=forum_topic.unread_mentions_count,
            unread_reactions_count=forum_topic.unread_reactions_count,
            unread_poll_vote_count=forum_topic.unread_poll_votes_count,
            is_my=forum_topic.my,
            is_closed=forum_topic.closed,
            is_pinned=forum_topic.pinned,
            is_short=forum_topic.short,
            is_hidden=forum_topic.hidden,
        )

    @staticmethod
    async def _parse_message(
        client: pyrogram.Client,
        message: raw.base.Message,
        users: dict[int, raw.base.User] | None = None,
        chats: dict[int, raw.base.Chat] | None = None,
    ) -> ForumTopic | None:
        if chats is None:
            chats = {}
        if users is None:
            users = {}

        if isinstance(message, raw.types.MessageService) and isinstance(
            message.action, (raw.types.MessageActionTopicCreate, raw.types.MessageActionTopicEdit)
        ):
            topic_id = message.id

            if message.reply_to:
                topic_id = message.reply_to.reply_to_top_id

            peer_id = utils.get_raw_peer_id(message.from_id)

            return ForumTopic(
                id=topic_id,
                name=message.action.title,
                date=utils.timestamp_to_datetime(message.date),
                icon_color=getattr(message.action, "icon_color", None),
                icon_custom_emoji_id=str(message.action.icon_emoji_id),
                creator=await types.Chat._parse_chat(
                    client, users.get(peer_id) or chats.get(peer_id)
                ),
                is_closed=getattr(message.action, "closed", None),
                is_hidden=getattr(message.action, "hidden", None),
            )

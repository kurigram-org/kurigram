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
from pyrogram import raw, types, utils

from ..object import Object
from ..update import Update


class WidgetQuery(Object, Update):
    """This object represents an incoming query from a widget in a message sent by the bot or via the bot.

    Use :meth:`~pyrogram.Client.answer_widget_query` to answer the query.
    Each user can send at most 5 queries per 5 seconds to the bot from all its widgets.

    Parameters:
        id (``str``):
            Unique identifier for this query.

        from_user (:obj:`~pyrogram.types.User`):
            Sender.

        chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Chat with the message containing the widget.
            Omitted if the widget is in an inline message.

        message_id (``int``, *optional*):
            Identifier of the message containing the widget.
            Omitted if the widget is in an inline message.

        inline_message_id (``str``, *optional*):
            Identifier of the inline message containing the widget.

        chat_instance (``str``):
            Global identifier, uniquely corresponding to the chat to which the message with the widget was sent.

        chat_type (``str``, *optional*):
            For widgets in inline messages, type of the chat to which the message was sent.
            Can be either ``sender`` for a private chat with the inline query sender, ``private``, ``group``,
            ``supergroup``, or ``channel``.

        type (:obj:`~pyrogram.types.WidgetQueryType`):
            Type of the query.

        data (``str`` | ``bytes``):
            Data of the query, 1-64 bytes.

        widget_id (``str``, *optional*):
            Unique identifier of the shared widget, which sent the query.
            Omitted if the widget isn't shared.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: str,
        from_user: types.User,
        chat: types.Chat | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        chat_instance: str,
        chat_type: str | None = None,
        type: types.WidgetQueryType,
        data: str | bytes,
        widget_id: str | None = None,
    ) -> None:
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.chat = chat
        self.message_id = message_id
        self.inline_message_id = inline_message_id
        self.chat_instance = chat_instance
        self.chat_type = chat_type
        self.type = type
        self.data = data
        self.widget_id = widget_id

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        query: raw.types.UpdateBotWidgetQuery | raw.types.UpdateInlineBotWidgetQuery,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> WidgetQuery:
        chat = None
        message_id = None
        inline_message_id = None
        chat_type = None

        if isinstance(query, raw.types.UpdateBotWidgetQuery):
            peer_id = utils.get_raw_peer_id(query.peer)
            peer = (
                users.get(peer_id)
                if isinstance(query.peer, raw.types.PeerUser)
                else chats.get(peer_id)
            )
            chat = await types.Chat._parse_chat(client, peer)
            message_id = query.msg_id
        else:
            inline_message_id = utils.pack_inline_message_id(query.inline_message_id)
            chat_type = query.chat_type or None

        try:
            data = query.data.decode()
        except UnicodeDecodeError:
            data = query.data

        return WidgetQuery(
            id=str(query.query_id),
            from_user=await types.User._parse(client, users.get(query.user_id)),
            chat=chat,
            message_id=message_id,
            inline_message_id=inline_message_id,
            chat_instance=str(query.chat_instance),
            chat_type=chat_type,
            type=await types.WidgetQueryType._parse(
                client, query.query_type, query.wallet_card, users, chats
            ),
            data=data,
            widget_id=str(query.widget_id) if query.widget_id else None,
            client=client,
        )


class SharedWidgetQuery(Object, Update):
    """This object represents an incoming query from a forwarded message with a shared widget created by the bot.

    Use :meth:`~pyrogram.Client.answer_widget_query` to answer the query.
    Each user can send at most 5 queries per 5 seconds to the bot from all its widgets.

    Parameters:
        id (``str``):
            Unique identifier for this query.

        from_user (:obj:`~pyrogram.types.User`):
            Sender.

        type (:obj:`~pyrogram.types.WidgetQueryType`):
            Type of the query.

        data (``str`` | ``bytes``):
            Data of the query, 1-64 bytes.

        widget_id (``str``):
            Unique identifier of the shared widget, which sent the query.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        id: str,
        from_user: types.User,
        type: types.WidgetQueryType,
        data: str | bytes,
        widget_id: str,
    ) -> None:
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.type = type
        self.data = data
        self.widget_id = widget_id

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        query: raw.types.UpdateBotWidgetCopyQuery,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> SharedWidgetQuery:
        try:
            data = query.data.decode()
        except UnicodeDecodeError:
            data = query.data

        return SharedWidgetQuery(
            id=str(query.query_id),
            from_user=await types.User._parse(client, users.get(query.user_id)),
            type=await types.WidgetQueryType._parse(
                client, query.query_type, query.wallet_card, users, chats
            ),
            data=data,
            widget_id=str(query.widget_id),
            client=client,
        )

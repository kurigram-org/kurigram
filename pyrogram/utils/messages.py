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
from pyrogram import enums, raw, types

from .peers import get_channel_id, get_peer_id, get_raw_peer_id
from .text import parse_text_entities


async def parse_messages(
    client: pyrogram.Client,
    messages: raw.base.messages.Messages | raw.base.Updates,
    replies: int = 1,
) -> list[types.Message]:
    users = {i.id: i for i in getattr(messages, "users", [])}
    chats = {i.id: i for i in getattr(messages, "chats", [])}
    topics = {i.id: i for i in getattr(messages, "topics", [])}

    parsed_messages = []

    if isinstance(
        messages,
        (
            raw.types.messages.ChannelMessages,
            raw.types.messages.Messages,
            raw.types.messages.MessagesNotModified,
            raw.types.messages.MessagesSlice,
        ),
    ):
        if not messages.messages:
            return types.List()

        for message in messages.messages:
            parsed_messages.append(
                await types.Message._parse(
                    client=client,
                    message=message,
                    users=users,
                    chats=chats,
                    topics=topics,
                    replies=0,
                )
            )

        if replies:
            messages_with_replies = {}
            messages_with_story_replies = {}

            for m in messages.messages:
                if isinstance(m, raw.types.MessageEmpty):
                    continue

                if m.reply_to and isinstance(m.reply_to, raw.types.MessageReplyHeader):
                    messages_with_replies[m.id] = m.reply_to

                if m.reply_to and isinstance(m.reply_to, raw.types.MessageReplyStoryHeader):
                    messages_with_story_replies[m.id] = m.reply_to

            if messages_with_replies:
                # We need a chat id, but some messages might be empty (no chat attribute available)
                # Scan until we find a message with a chat available (there must be one, because we are fetching replies)
                chat_id = next(
                    (m.chat.id for m in parsed_messages if m.chat and m.chat.id is not None),
                    0,
                )

                is_all_replies_in_same_chat = not any(
                    m.reply_to_peer_id for m in messages_with_replies.values()
                )
                reply_messages: list[types.Message] = []

                if is_all_replies_in_same_chat:
                    reply_messages = await client.get_messages(
                        chat_id=chat_id,
                        message_ids=list(messages_with_replies.keys()),
                        reply=True,
                        replies=replies - 1,
                    )
                else:
                    for reply_header in messages_with_replies.values():
                        reply_messages.append(
                            await client.get_messages(
                                chat_id=get_peer_id(reply_header.reply_to_peer_id)
                                if getattr(reply_header, "reply_to_peer_id", None)
                                else chat_id,
                                message_ids=reply_header.reply_to_msg_id,
                                replies=replies - 1,
                            )
                        )

                for message in parsed_messages:
                    reply_to = messages_with_replies.get(message.id, None)

                    if not reply_to:
                        continue

                    for reply in reply_messages:
                        if reply.id == reply_to.reply_to_msg_id:
                            message.reply_to_message = reply
    else:
        for u in getattr(messages, "updates", []):
            if isinstance(
                u,
                (
                    raw.types.UpdateNewMessage,
                    raw.types.UpdateNewChannelMessage,
                    raw.types.UpdateNewScheduledMessage,
                    raw.types.UpdateBotNewBusinessMessage,
                    raw.types.UpdateNewEphemeralMessage,
                    raw.types.UpdateEditMessage,
                    raw.types.UpdateEditChannelMessage,
                    raw.types.UpdateEditEphemeralMessage,
                ),
            ):
                parsed_messages.append(
                    await types.Message._parse(
                        client,
                        u.message,
                        users,
                        chats,
                        is_scheduled=isinstance(u, raw.types.UpdateNewScheduledMessage),
                        business_connection_id=getattr(u, "connection_id", None),
                        raw_reply_to_message=getattr(u, "reply_to_message", None),
                        replies=replies,
                    )
                )

    return types.List(parsed_messages)


async def parse_deleted_messages(client, update, users, chats) -> list[types.Message]:
    is_ephemeral = isinstance(update, raw.types.UpdateDeleteEphemeralMessages)

    messages = update.ids if is_ephemeral else update.messages
    channel_id = getattr(update, "channel_id", None)
    peer = getattr(update, "peer", None)

    chat = None

    if channel_id:
        chat = types.Chat(id=get_channel_id(channel_id), type=enums.ChatType.CHANNEL, client=client)
    if peer:
        chat_id = get_raw_peer_id(peer)
        if chat_id:
            if isinstance(peer, raw.types.PeerUser):
                chat = await types.Chat._parse_user_chat(client, users[chat_id])

            elif isinstance(peer, raw.types.PeerChat):
                chat = await types.Chat._parse_chat_chat(client, chats[chat_id])

            else:
                chat = await types.Chat._parse_channel_chat(client, chats[chat_id])

    parsed_messages = [
        types.Message(
            id=0 if is_ephemeral else message,
            ephemeral_message_id=message if is_ephemeral else None,
            chat=chat,
            business_connection_id=getattr(update, "connection_id", None),
            client=client,
        )
        for message in messages
    ]

    return types.List(parsed_messages)


async def get_reply_to(
    client: pyrogram.Client,
    reply_parameters: types.ReplyParameters | None = None,
    message_thread_id: int | None = None,
    direct_messages_topic_id: int | None = None,
) -> raw.base.InputReplyTo | None:
    """Get InputReply for reply_to argument"""
    if reply_parameters:
        if reply_parameters.chat_id and reply_parameters.story_id:
            return raw.types.InputReplyToStory(
                peer=await client.resolve_peer(reply_parameters.chat_id),
                story_id=reply_parameters.story_id,
            )

        if reply_parameters.message_id:
            message = None
            entities = None

            if reply_parameters.quote:
                message, entities = (
                    await parse_text_entities(
                        client,
                        reply_parameters.quote,
                        reply_parameters.quote_parse_mode,
                        reply_parameters.quote_entities,
                    )
                ).values()

            return raw.types.InputReplyToMessage(
                reply_to_msg_id=reply_parameters.message_id,
                top_msg_id=message_thread_id,
                reply_to_peer_id=await client.resolve_peer(reply_parameters.chat_id),
                quote_text=message,
                quote_entities=entities,
                quote_offset=reply_parameters.quote_position,
                monoforum_peer_id=await client.resolve_peer(direct_messages_topic_id),
                todo_item_id=reply_parameters.checklist_task_id,
                poll_option=reply_parameters.poll_option_id.encode()
                if reply_parameters.poll_option_id is not None
                else None,
            )

        if reply_parameters.ephemeral_message_id:
            return raw.types.InputReplyToEphemeralMessage(id=reply_parameters.ephemeral_message_id)

    if message_thread_id:
        return raw.types.InputReplyToMessage(reply_to_msg_id=message_thread_id)

    if direct_messages_topic_id:
        return raw.types.InputReplyToMonoForum(
            monoforum_peer_id=await client.resolve_peer(direct_messages_topic_id)
        )

    return None

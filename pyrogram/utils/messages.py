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


async def get_message_min_peer_ids(
    client: pyrogram.Client, message: types.Message
) -> set[int] | None:
    """Get the ids of the `min` users and channels a parsed message references.

    Returns:
        ``None`` when the message cannot be used to address a `min` peer, that is: the account
        is a bot, the message is scheduled, or it is not in a channel or supergroup.
        Otherwise the set of marked ids, which is empty when no referenced peer is `min`.
    """
    # Scheduled messages are left out, their ids are not ids of messages in the chat.
    if message.scheduled or message.chat is None:
        return None

    # Only channels and supergroups: "Usually `min` constructors are encountered in messages
    #  inside of groups or channels" (https://core.telegram.org/api/min), and TDLib records
    #  them for no other dialog type:
    #  https://github.com/tdlib/td/blob/42e6a5259551178d1dab54a22ad96d14bd906e20/td/telegram/UserManager.cpp#L7795-L7797
    #  https://github.com/tdlib/td/blob/42e6a5259551178d1dab54a22ad96d14bd906e20/td/telegram/MessagesManager.cpp#L31561-L31566
    #  A monoforum (`DIRECT`) is left out as well: `CHANNEL_MONOFORUM_UNSUPPORTED` is listed
    #  among the errors of `users.getUsers`, https://core.telegram.org/method/users.getUsers
    if message.chat.type not in (
        enums.ChatType.CHANNEL,
        enums.ChatType.SUPERGROUP,
        enums.ChatType.FORUM,
    ):
        return None

    # Bots get `FROM_MESSAGE_BOT_DISABLED` for these and use `access_hash=0` instead:
    #  https://core.telegram.org/api/peers
    #  `me` is in memory once `start()` has loaded it, the storage is read only until then.
    if client.me.is_bot if client.me else await client.storage.is_bot():
        return None

    # "sender, forwarder or forwardee, et cetera": `from_id`, `fwd_from` and
    #  `messageEntityMentionName`, per https://core.telegram.org/api/min
    peers: list[types.Chat | types.User] = []

    # `sender_chat` is only parsed when there is no `from_user`, so they never both apply.
    if message.from_user is not None:
        peers.append(message.from_user)
    elif message.sender_chat is not None:
        peers.append(message.sender_chat)

    # A hidden user or an imported message carries no peer to address.
    origin = message.forward_origin
    origin_peer = (
        origin.sender_user
        if isinstance(origin, types.MessageOriginUser)
        else origin.sender_chat
        if isinstance(origin, types.MessageOriginChat)
        else origin.chat
        if isinstance(origin, types.MessageOriginChannel)
        else None
    )

    if origin_peer is not None:
        peers.append(origin_peer)

    # Only text mentions carry a `user`, `MessageEntity._parse` fills it from the `user_id`.
    for entities in (message.entities, message.caption_entities):
        peers.extend(entity.user for entity in entities or () if entity.user is not None)

    # Only `min` objects: a full one is stored with a real `access_hash`, which `resolve_peer`
    #  reads before this cache. A channel posting in itself is not a sighting in another chat.
    return {
        peer.id
        for peer in peers
        if peer.id is not None and peer.is_min and peer.id != message.chat.id
    }


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

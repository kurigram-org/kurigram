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

import re
from typing import Final

import pyrogram
from pyrogram import raw, utils
from pyrogram.errors import (
    ChannelInvalid,
    ChannelMonoforumUnsupported,
    ChannelPrivate,
    MsgIdInvalid,
    PeerIdInvalid,
    UserBannedInChannel,
)

# What `users.getUsers` and `channels.getChannels` answer when the sighting itself can no
#  longer be used: the message is gone, or its chat is out of this account's reach. Any
#  other error has nothing to do with the sighting, so it is raised as usual, including
#  `FROM_MESSAGE_BOT_DISABLED`, which a bot never gets since nothing is recorded for it.
#  https://core.telegram.org/method/users.getUsers
#  https://core.telegram.org/method/channels.getChannels
_STALE_SIGHTING_ERRORS: Final[tuple[type[Exception], ...]] = (
    ChannelInvalid,
    ChannelMonoforumUnsupported,
    ChannelPrivate,
    MsgIdInvalid,
    PeerIdInvalid,
    UserBannedInChannel,
)


async def _resolve_min_peer(
    client: pyrogram.Client, peer_id: int, peer_type: str
) -> raw.base.InputPeer | None:
    """Resolve a `min` user or channel through the messages it was last seen in.

    The sightings are the ones `Client.min_peer_cache` recorded while parsing messages. The
    newest is tried first. Its message is sent to the server with the peer, so a stale one
    surfaces here as an error (`MSG_ID_INVALID` and the like). A sighting that is stale, whose
    chat is not in the storage, or whose answer does not contain the peer, is forgotten and the
    next newest is tried. `None` means no sighting worked.
    """
    raw_peer_id = utils.get_raw_peer_id(peer_id)

    for sighting in await client.min_peer_cache.get(peer_id):
        chat_id, message_id = sighting.chat_id, sighting.message_id

        # TDLib records a sighting only when its channel is known, so one whose chat is not
        #  stored is as unusable as a stale one:
        #  https://github.com/tdlib/td/blob/42e6a5259551178d1dab54a22ad96d14bd906e20/td/telegram/UserManager.cpp#L7795-L7800
        try:
            chat_peer = await client.storage.get_peer_by_id(chat_id)
        except KeyError:
            await client.min_peer_cache.discard(peer_id, chat_id, message_id)
            continue

        try:
            if peer_type == "user":
                users = await client.invoke(
                    raw.functions.users.GetUsers(
                        id=[
                            raw.types.InputUserFromMessage(
                                peer=chat_peer, msg_id=message_id, user_id=raw_peer_id
                            )
                        ]
                    )
                )
                await client.fetch_peers(users)

                answered = any(
                    isinstance(user, raw.types.User) and user.id == raw_peer_id for user in users
                )
            else:
                chats = await client.invoke(
                    raw.functions.channels.GetChannels(
                        id=[
                            raw.types.InputChannelFromMessage(
                                peer=chat_peer, msg_id=message_id, channel_id=raw_peer_id
                            )
                        ]
                    )
                )

                answered = any(
                    isinstance(chat, (raw.types.Channel, raw.types.ChannelForbidden))
                    and chat.id == raw_peer_id
                    for chat in chats.chats
                )
        except _STALE_SIGHTING_ERRORS:
            answered = False

        # A success without the peer in it is no better than an error: an empty vector, or
        #  `userEmpty` for a deleted account, gives nothing to address.
        if not answered:
            await client.min_peer_cache.discard(peer_id, chat_id, message_id)
            continue

        # Asking through the sighting is what TDLib does for channels too
        #  (`ChatManager::register_message_channels`): when the answer is a full object,
        #  its real `access_hash` is now stored and outlives the message.
        #  https://github.com/tdlib/td/blob/42e6a5259551178d1dab54a22ad96d14bd906e20/td/telegram/ChatManager.cpp#L4376-L4390
        try:
            return await client.storage.get_peer_by_id(peer_id)
        except KeyError:
            pass

        # The answer was `min` again, so nothing was stored. The server still answered with the
        #  peer through this sighting, which makes it the peer to hand out.
        if peer_type == "user":
            return raw.types.InputPeerUserFromMessage(
                peer=chat_peer, msg_id=message_id, user_id=raw_peer_id
            )

        return raw.types.InputPeerChannelFromMessage(
            peer=chat_peer, msg_id=message_id, channel_id=raw_peer_id
        )

    return None


class ResolvePeer:
    async def resolve_peer(self: pyrogram.Client, peer_id: int | str) -> raw.base.InputPeer | None:
        """Get the InputPeer of a known peer id. Useful whenever an InputPeer type is required.

        .. note::

            This is a utility method intended to be used **only** when working with raw
            :obj:`functions <pyrogram.raw.functions>` (i.e: a Telegram API method you wish to use which is not
            available yet in the Client class as an easy-to-use method).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            peer_id (``int`` | ``str``):
                The peer id you want to extract the InputPeer from.
                Can be a direct id (int), a username (str), a link (str) or a phone number (str).

        Returns:
            :obj:`~pyrogram.raw.base.InputPeer` | ``None``: On success, the resolved peer id is returned in
            form of an InputPeer object, otherwise, in case *peer_id* is None, None is returned.
            A user or channel only ever seen inside groups and channels (a "min" peer) is resolved
            through the last message it was seen in, and may come back as
            :obj:`~pyrogram.raw.types.InputPeerUserFromMessage` or
            :obj:`~pyrogram.raw.types.InputPeerChannelFromMessage`.

        Raises:
            KeyError: In case the peer doesn't exist in the internal database.
        """
        if not self.is_connected:
            raise ConnectionError("Client has not been started yet")

        if peer_id is None:
            return None

        if peer_id in ("self", "me"):
            return raw.types.InputPeerSelf()

        if peer_id == "empty":
            return raw.types.InputPeerEmpty()

        if isinstance(peer_id, int):
            try:
                return await self.storage.get_peer_by_id(peer_id)
            except KeyError:
                peer_type = utils.get_peer_type(peer_id)

                # Tried before the `access_hash=0` requests below. A bot records no sightings, so
                #  it always falls through to them: https://core.telegram.org/api/peers
                if peer_type in ("user", "channel"):
                    peer = await _resolve_min_peer(self, peer_id, peer_type)

                    if peer is not None:
                        return peer

                if peer_type == "user":
                    await self.fetch_peers(
                        await self.invoke(
                            raw.functions.users.GetUsers(
                                id=[
                                    raw.types.InputUser(
                                        user_id=utils.get_raw_peer_id(peer_id), access_hash=0
                                    )
                                ]
                            )
                        )
                    )
                elif peer_type == "chat":
                    await self.invoke(
                        raw.functions.messages.GetChats(id=[utils.get_raw_peer_id(peer_id)])
                    )
                else:
                    await self.invoke(
                        raw.functions.channels.GetChannels(
                            id=[
                                raw.types.InputChannel(
                                    channel_id=utils.get_raw_peer_id(peer_id), access_hash=0
                                )
                            ]
                        )
                    )

                try:
                    return await self.storage.get_peer_by_id(peer_id)
                except KeyError as e:
                    raise PeerIdInvalid from e
        elif isinstance(peer_id, str):
            phone = re.sub(r"[+()\s-]", "", peer_id)

            if phone.isdigit():
                try:
                    return await self.storage.get_peer_by_phone_number(phone)
                except KeyError:
                    r = await self.invoke(raw.functions.contacts.ResolvePhone(phone=phone))

                    return await self.storage.get_peer_by_id(utils.get_peer_id(r.peer))
            else:
                username = None
                channel_id = None

                match = self.CHANNEL_MESSAGE_LINK_RE.match(peer_id.lower())

                if match:
                    try:
                        channel_id = utils.get_channel_id(int(match.group(1)))
                    except ValueError:
                        username = match.group(1)
                else:
                    username = re.sub(r"[@+\s]", "", peer_id.lower())

                if channel_id:
                    try:
                        return await self.storage.get_peer_by_id(channel_id)
                    except KeyError as e:
                        raise PeerIdInvalid from e
                elif username:
                    try:
                        return await self.storage.get_peer_by_username(username)
                    except KeyError:
                        r = await self.invoke(
                            raw.functions.contacts.ResolveUsername(username=username)
                        )

                        return await self.storage.get_peer_by_id(utils.get_peer_id(r.peer))
                else:
                    raise PeerIdInvalid
        else:
            raise PeerIdInvalid

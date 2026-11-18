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

import re

import pyrogram
from pyrogram import raw, utils, enums
from pyrogram.errors import PeerIdInvalid


class ResolvePeer:
    async def _resolve_peer_from_message_cache(
        self: pyrogram.Client,
        peer_id: int | str,
    ) -> raw.types.InputPeerUserFromMessage | raw.types.InputPeerChannelFromMessage | None:
        for (_, message_id), parsed_message in self.message_cache._cache.items():
            if not parsed_message:
                continue

            if parsed_message.chat.type not in (
                enums.ChatType.GROUP,
                enums.ChatType.SUPERGROUP,
                enums.ChatType.FORUM,
            ):
                continue

            raw_message = parsed_message.raw

            sender = parsed_message.from_user or parsed_message.sender_chat

            if sender is None:
                continue

            raw_sender_id = utils.get_raw_peer_id(raw_message.from_id or raw_message.peer_id)

            if isinstance(peer_id, str):
                normalized_peer_id = peer_id.lstrip("@").lower()

                if (
                    not (sender.username and sender.username.lower() == normalized_peer_id)
                    and not any(
                        username.username.lower() == normalized_peer_id
                        for username in (sender.usernames or [])
                    )
                    and not (
                        getattr(sender, "phone_number", None)
                        and re.sub(r"\D", "", sender.phone_number) == re.sub(r"\D", "", peer_id)
                    )
                ):
                    continue

            elif sender.id != peer_id:
                continue

            if isinstance(raw_message.peer_id, raw.types.PeerUser):
                input_peer = raw.types.InputPeerUser(
                    user_id=utils.get_raw_peer_id(peer=raw_message.peer_id),
                    access_hash=parsed_message.chat.raw.access_hash,
                )
            elif isinstance(raw_message.peer_id, raw.types.PeerChat):
                input_peer = raw.types.InputPeerChat(
                    chat_id=utils.get_raw_peer_id(peer=raw_message.peer_id),
                )
            elif isinstance(raw_message.peer_id, raw.types.PeerChannel):
                input_peer = raw.types.InputPeerChannel(
                    channel_id=utils.get_raw_peer_id(peer=raw_message.peer_id),
                    access_hash=parsed_message.chat.raw.access_hash,
                )
            else:
                continue

            if parsed_message.from_user:
                return raw.types.InputPeerUserFromMessage(
                    peer=input_peer, msg_id=message_id, user_id=raw_sender_id
                )
            elif parsed_message.sender_chat:
                return raw.types.InputPeerChannelFromMessage(
                    peer=input_peer, msg_id=message_id, channel_id=raw_sender_id
                )

        return None

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
                    from_message = await self._resolve_peer_from_message_cache(peer_id=peer_id)

                    if from_message is not None:
                        return from_message

                    raise PeerIdInvalid from e
        elif isinstance(peer_id, str):
            phone = re.sub(r"[+()\s-]", "", peer_id)

            if phone.isdigit():
                try:
                    return await self.storage.get_peer_by_phone_number(phone)
                except KeyError:
                    r = await self.invoke(raw.functions.contacts.ResolvePhone(phone=phone))

                    try:
                        return await self.storage.get_peer_by_id(utils.get_peer_id(r.peer))
                    except KeyError as e:
                        from_message = await self._resolve_peer_from_message_cache(peer_id=phone)

                        if from_message is not None:
                            return from_message

                        raise PeerIdInvalid from e
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
                        from_message = await self._resolve_peer_from_message_cache(
                            peer_id=channel_id
                        )

                        if from_message is not None:
                            return from_message

                        raise PeerIdInvalid from e
                elif username:
                    try:
                        return await self.storage.get_peer_by_username(username)
                    except KeyError:
                        r = await self.invoke(
                            raw.functions.contacts.ResolveUsername(username=username)
                        )

                        try:
                            return await self.storage.get_peer_by_id(utils.get_peer_id(r.peer))
                        except KeyError as e:
                            from_message = await self._resolve_peer_from_message_cache(
                                peer_id=username
                            )

                            if from_message is not None:
                                return from_message

                            raise PeerIdInvalid from e
                else:
                    raise PeerIdInvalid
        else:
            raise PeerIdInvalid

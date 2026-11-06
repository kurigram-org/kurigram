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

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def _access_hash_in(peers: list[raw.base.User] | list[raw.base.Chat], peer_id: int | None) -> int:
    """Get the `access_hash` an answer's `users` or `chats` carries for `peer_id`, `0` if none."""
    for peer in peers:
        if (
            isinstance(peer, (raw.types.User, raw.types.Channel, raw.types.ChannelForbidden))
            and peer.id == peer_id
        ):
            return peer.access_hash or 0

    return 0


async def get_chunk(
    client: pyrogram.Client,
    peer: raw.types.InputPeerChannel | raw.types.InputPeerChannelFromMessage,
    peer_id: int,
    peer_access_hash: int,
    offset: int = 0,
    limit: int = 100,
) -> list[types.ChatPhoto]:
    r = await client.invoke(
        raw.functions.messages.Search(
            peer=peer,
            q="",
            filter=raw.types.InputMessagesFilterChatPhotos(),
            min_date=0,
            max_date=0,
            offset_id=0,
            add_offset=offset,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0,
        ),
        sleep_threshold=60,
    )

    photos = []

    for message in r.messages:
        if not isinstance(message, raw.types.MessageService):
            continue

        if not isinstance(message.action, raw.types.MessageActionChatEditPhoto):
            continue

        photos.append(
            await types.ChatPhoto._parse(
                client=client,
                chat_photo=message.action.photo,
                peer_id=peer_id,
                peer_access_hash=peer_access_hash,
            )
        )

    return photos


class GetChatPhotos:
    async def get_chat_photos(
        self: pyrogram.Client,
        chat_id: int | str,
        limit: int = 0,
    ) -> AsyncGenerator[types.ChatPhoto, None]:
        """Get a chat or a user profile photos sequentially.
        Personal and public photo aren't returned.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            limit (``int``, *optional*):
                Limits the number of profile photos to be retrieved.
                By default, no limit is applied and all profile photos are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.ChatPhoto` objects.

        Example:
            .. code-block:: python

                async for photo in app.get_chat_photos("me"):
                    print(photo)
        """
        peer = await self.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerSelf):
            peer_id = self.me.id if self.me else None
            peer_access_hash = 0
        else:
            peer_id = utils.get_raw_peer_id(peer)
            # A `*FromMessage` peer carries none: it is taken from the answers below, whose
            #  `min` one is still valid for profile photos (https://core.telegram.org/api/min).
            #  TDLib keeps it the same way, off the answer's own `users`:
            #  https://github.com/tdlib/td/blob/42e6a5259551178d1dab54a22ad96d14bd906e20/td/telegram/UserManager.cpp#L1521
            #  Only a photo without a concrete size keeps an id that carries it
            #  (`ChatPhoto._parse()`), every other one is downloaded by its own `access_hash`.
            peer_access_hash = getattr(peer, "access_hash", 0)

        current = 0
        total = limit or (1 << 31)
        limit = min(100, total)
        offset = 0

        if isinstance(peer, utils.PEERS_WITH_A_CHANNEL_ID):
            current_photo = None

            r = await self.invoke(
                raw.functions.channels.GetFullChannel(channel=utils.get_input_user_or_channel(peer))
            )

            if isinstance(peer, raw.types.InputPeerChannelFromMessage):
                peer_access_hash = _access_hash_in(r.chats, peer_id)

            if not isinstance(r.full_chat.chat_photo, raw.types.PhotoEmpty):
                current_photo = await types.ChatPhoto._parse(
                    client=self,
                    chat_photo=r.full_chat.chat_photo,
                    peer_id=peer_id,
                    peer_access_hash=peer_access_hash,
                )

                yield current_photo

                current += 1

                if current >= total:
                    return

            if self.me and not self.me.is_bot:
                while True:
                    photos = await get_chunk(
                        client=self,
                        peer=peer,
                        peer_id=peer_id,
                        peer_access_hash=peer_access_hash,
                        offset=offset,
                        limit=limit,
                    )

                    if not photos:
                        return

                    offset += len(photos)

                    for photo in photos:
                        if current_photo and current_photo.big_file_id == photo.big_file_id:
                            continue

                        yield photo

                        current += 1

                        if current >= total:
                            return

                    if len(photos) < limit:
                        return

        else:
            while True:
                r = await self.invoke(
                    raw.functions.photos.GetUserPhotos(
                        user_id=utils.get_input_user_or_channel(peer),
                        offset=offset,
                        max_id=0,
                        limit=limit,
                    )
                )

                if isinstance(peer, raw.types.InputPeerUserFromMessage):
                    peer_access_hash = _access_hash_in(r.users, peer_id) or peer_access_hash

                photos = [
                    await types.ChatPhoto._parse(
                        client=self,
                        chat_photo=photo,
                        peer_id=peer_id,
                        peer_access_hash=peer_access_hash,
                    )
                    for photo in r.photos
                ]

                if not photos:
                    return

                offset += len(photos)

                for photo in photos:
                    yield photo

                    current += 1

                    if current >= total:
                        return

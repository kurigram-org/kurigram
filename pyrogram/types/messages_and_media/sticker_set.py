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

from ..object import Object


class StickerSet(Object):
    """This object represents a sticker set.

    Parameters:
        id (``int``):
            Unique identifier for this sticker set.

        name (``str``):
            Identifier for this file, which can be used to download or reuse the file.

        title (``str``):
            Unique identifier for this file, which is supposed to be the same over time and for different accounts.
            Can't be used to download or reuse the file.

        sticker_type (:obj:`~pyrogram.enums.StickerType`):
            Type of stickers in the set.

        stickers (List of :obj:`~pyrogram.types.Sticker`, *optional*):
            List of all set stickers.

        thumbs (List of :obj:`~pyrogram.types.Thumbnail`, *optional*):
            Sticker set thumbnail in the .WEBP, .TGS, or .WEBM format.

        is_owned (``bool``, *optional*):
            True, if the user is the owner of the sticker set.

        is_installed (``bool``, *optional*):
            True, if the sticker set is installed.

        is_archived (``bool``, *optional*):
            True, if the sticker set has been archived.

        is_official (``bool``, *optional*):
            True, if the sticker set is official.

        is_allowed_as_chat_emoji_status (``bool``, *optional*):
            True, if the sticker set is allowed to be used as chat emoji status.

        needs_repainting (``bool``, *optional*):
            True, if the sticker set needs to be repainted.

        raw (:obj:`~pyrogram.raw.base.StickerSet`, *optional*):
            The raw object.
    """

    def __init__(
        self,
        *,
        id: int,
        name: str,
        title: str,
        sticker_type: enums.StickerType,
        stickers: list[types.Sticker] | None = None,
        thumbs: list[types.Thumbnail] | None = None,
        is_owned: bool | None = None,
        is_installed: bool | None = None,
        is_archived: bool | None = None,
        is_official: bool | None = None,
        is_allowed_as_chat_emoji_status: bool | None = None,
        needs_repainting: bool | None = None,
        raw: raw.types.Document | None = None,
    ):
        super().__init__()

        self.id = id
        self.name = name
        self.title = title
        self.sticker_type = sticker_type
        self.stickers = stickers
        self.thumbs = thumbs
        self.is_owned = is_owned
        self.is_installed = is_installed
        self.is_archived = is_archived
        self.is_official = is_official
        self.is_allowed_as_chat_emoji_status = is_allowed_as_chat_emoji_status
        self.needs_repainting = needs_repainting
        self.raw = raw

    @property
    def link(self) -> str:
        return f"https://t.me/addstickers/{self.name}"

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        sticker_set: raw.types.messages.StickerSet | raw.types.StickerSet,
    ) -> StickerSet:
        if isinstance(sticker_set, raw.types.StickerSet):
            return await StickerSet._parse_set(client, sticker_set)

        if isinstance(sticker_set, raw.types.messages.StickerSet):
            return await StickerSet._parse_messages_set(client, sticker_set)

    @staticmethod
    async def _parse_messages_set(
        client: pyrogram.Client,
        sticker_set: raw.types.messages.StickerSet,
    ) -> StickerSet:
        _set: raw.types.StickerSet = sticker_set.set
        documents = {i.id: i for i in sticker_set.documents}

        sticker_type = enums.StickerType.REGULAR

        if _set.masks:
            sticker_type = enums.StickerType.MASK
        elif _set.emojis:
            sticker_type = enums.StickerType.CUSTOM_EMOJI

        thumb = documents.get(_set.thumb_document_id)

        if thumb is None:
            if _set.thumb_document_id:
                r = await client.invoke(
                    raw.functions.messages.GetCustomEmojiDocuments(
                        document_id=[_set.thumb_document_id]
                    )
                )

                thumb = r[0]
            else:
                thumb = sticker_set.documents[0]

        await client.sticker_set_name_cache.set((_set.id, _set.access_hash), _set.short_name)

        return StickerSet(
            id=_set.id,
            name=_set.short_name,
            title=_set.title,
            sticker_type=sticker_type,
            stickers=types.List(
                [
                    await types.Sticker._parse(client, doc, {type(a): a for a in doc.attributes})
                    for doc in sticker_set.documents
                ]
            ),
            thumbs=types.Thumbnail._parse(client, thumb),
            is_owned=_set.creator,
            is_installed=bool(_set.installed_date),
            is_archived=_set.archived,
            is_official=_set.official,
            is_allowed_as_chat_emoji_status=_set.channel_emoji_status,
            needs_repainting=_set.text_color,
            raw=sticker_set,
        )

    @staticmethod
    async def _parse_set(
        client: pyrogram.Client,
        sticker_set: raw.types.StickerSet,
    ) -> StickerSet:
        sticker_type = enums.StickerType.REGULAR

        if sticker_set.masks:
            sticker_type = enums.StickerType.MASK
        elif sticker_set.emojis:
            sticker_type = enums.StickerType.CUSTOM_EMOJI

        await client.sticker_set_name_cache.set(
            (sticker_set.id, sticker_set.access_hash), sticker_set.short_name
        )

        return StickerSet(
            id=sticker_set.id,
            name=sticker_set.short_name,
            title=sticker_set.title,
            sticker_type=sticker_type,
            is_owned=sticker_set.creator,
            is_installed=bool(sticker_set.installed_date),
            is_archived=sticker_set.archived,
            is_official=sticker_set.official,
            is_allowed_as_chat_emoji_status=sticker_set.channel_emoji_status,
            needs_repainting=sticker_set.text_color,
            raw=sticker_set,
        )

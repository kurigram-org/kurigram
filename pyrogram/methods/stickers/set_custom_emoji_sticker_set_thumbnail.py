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
from pyrogram import raw, types


class SetCustomEmojiStickerSetThumbnail:
    async def set_custom_emoji_sticker_set_thumbnail(
        self: pyrogram.Client,
        name: str,
        custom_emoji_id: str = "",
    ) -> types.StickerSet:
        """Use this method to set the thumbnail of a custom emoji sticker set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            name (``str``):
                Name of the sticker set.

            custom_emoji_id (``bool``, *optional*):
                Custom emoji identifier of a sticker from the sticker set.
                Pass an empty string to drop the thumbnail and use the first sticker as the thumbnail.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: A updated sticker set is returned.
        """
        r = await self.invoke(
            raw.functions.stickers.SetStickerSetThumb(
                stickerset=raw.types.InputStickerSetShortName(short_name=name),
                thumb_document_id=int(custom_emoji_id) if custom_emoji_id else 0,
            )
        )

        return await types.StickerSet._parse(self, r)

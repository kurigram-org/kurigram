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

from typing import BinaryIO

import pyrogram
from pyrogram import enums, raw, types
from pyrogram._typing import PathType


class SetStickerSetThumbnail:
    async def set_sticker_set_thumbnail(
        self: pyrogram.Client,
        user_id: int | str,
        name: str,
        format: enums.StickerFormat,
        thumbnail: PathType | BinaryIO | None = None,
    ) -> types.StickerSet:
        """Use this method to set the thumbnail of a regular or mask sticker set.
        The format of the thumbnail file must match the format of the stickers in the set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
               Unique identifier (int) or username (str) of sticker set owner.

            name (``str``):
                Name of the sticker set.

            format (:obj:`~pyrogram.enums.StickerFormat`):
                Format of the thumbnail.

            thumbnail (``str`` | ``os.PathLike`` | ``BinaryIO``, *optional*):
                Thumbnail to set.
                Pass None to remove the thumbnail.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: A updated sticker set is returned.
        """
        thumb = await types.InputSticker(
            sticker=thumbnail,
            format=format,
            emoji_list=[],
        ).write(client=self, chat_id=user_id)

        r = await self.invoke(
            raw.functions.stickers.SetStickerSetThumb(
                stickerset=raw.types.InputStickerSetShortName(short_name=name), thumb=thumb.document
            )
        )

        return await types.StickerSet._parse(self, r)

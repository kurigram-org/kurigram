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
from pyrogram import raw, types, utils
from pyrogram.file_id import FileType


class SetStickerMaskPosition:
    async def set_sticker_mask_position(
        self: pyrogram.Client, sticker: str, mask_position: types.MaskPosition | None = None
    ) -> types.StickerSet:
        """Use this method to change the mask position of a mask sticker.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str``):
                File identifier of the sticker.

            mask_position (:obj:`~pyrogram.types.MaskPosition`, *optional*):
                Position where the mask should be placed on faces.
                Omit the parameter to remove the mask position.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: A updated sticker set is returned.
        """
        r = await self.invoke(
            raw.functions.stickers.ChangeSticker(
                sticker=utils.get_input_media_from_file_id(
                    file_id=sticker, expected_file_type=FileType.STICKER
                ).id,
                mask_coords=mask_position.write() if mask_position else None,
            )
        )

        return await types.StickerSet._parse(self, r)

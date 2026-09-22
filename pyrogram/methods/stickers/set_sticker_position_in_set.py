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


class SetStickerPositionInSet:
    async def set_sticker_position_in_set(
        self: pyrogram.Client, sticker: str, position: int
    ) -> types.StickerSet:
        """Use this method to move a sticker in a set created by the bot to a specific position.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            sticker (``str``):
                File identifier of the sticker.

            position (``int``):
                New sticker position in the set, zero-based.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: A updated sticker set is returned.
        """
        r = await self.invoke(
            raw.functions.stickers.ChangeStickerPosition(
                sticker=utils.get_input_media_from_file_id(
                    file_id=sticker, expected_file_type=FileType.STICKER
                ).id,
                position=position,
            )
        )

        return await types.StickerSet._parse(self, r)

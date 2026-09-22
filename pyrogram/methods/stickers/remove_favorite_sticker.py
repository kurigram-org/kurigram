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
from pyrogram import raw, utils
from pyrogram.file_id import FileType


class RemoveFavoriteSticker:
    async def remove_favorite_sticker(self: pyrogram.Client, sticker: str) -> bool:
        """Removes a sticker from the list of favorite stickers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker (``str``):
                File identifier of the sticker.

        Returns:
            ``bool``: True, on success.
        """
        r = await self.invoke(
            raw.functions.messages.FaveSticker(
                id=utils.get_input_media_from_file_id(
                    file_id=sticker, expected_file_type=FileType.STICKER
                ).id,
                unfave=True,
            )
        )

        return bool(r)

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


class SetStickerSetTitle:
    async def set_sticker_set_title(
        self: pyrogram.Client, name: str, title: str
    ) -> types.StickerSet:
        """Use this method to set the title of a created sticker set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            name (``str``):
                Name of the sticker set.

            title (``str``):
                Sticker set title, 1-64 characters.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: A updated sticker set object is returned.

        Example:
            .. code-block:: python

                await app.set_sticker_set_title("my_sticker_set", "New title")
        """
        r = await self.invoke(
            raw.functions.stickers.RenameStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=name), title=title
            )
        )

        return await types.StickerSet._parse(self, r)

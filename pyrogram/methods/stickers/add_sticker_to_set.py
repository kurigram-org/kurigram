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


class AddStickerToSet:
    async def add_sticker_to_set(
        self: pyrogram.Client,
        user_id: int | str,
        name: str,
        sticker: types.InputSticker,
    ) -> types.StickerSet:
        """Adds a new sticker to a set.
        Emoji sticker sets can have up to 200 stickers.
        Other sticker sets can have up to 120 stickers.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
               Unique identifier (int) or username (str) of sticker file owner.

            name (``str``):
                Name of the sticker set.

            sticker (:obj:`~pyrogram.types.InputSticker`):
                Sticker to be added to the set.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: A updated sticker set is returned.

        Example:
            .. code-block:: python

                from pyrogram import enums

                await app.add_sticker_to_set(
                    "me",
                    "my_sticker_set",
                    sticker=types.InputSticker(
                        sticker="sticker.png",
                        format=enums.StickerFormat.STATIC,
                        emoji_list=["👍"]
                    )
                )
        """
        r = await self.invoke(
            raw.functions.stickers.AddStickerToSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=name),
                sticker=await sticker.write(client=self, chat_id=user_id),
            )
        )

        return await types.StickerSet._parse(self, r)

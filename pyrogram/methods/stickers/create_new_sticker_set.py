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
from pyrogram import raw, types, enums


class CreateNewStickerSet:
    async def create_new_sticker_set(
        self: pyrogram.Client,
        user_id: int | str,
        name: str,
        title: str,
        stickers: list[types.InputSticker],
        sticker_type: enums.StickerType = enums.StickerType.REGULAR,
        needs_repainting: bool | None = None,
    ) -> types.StickerSet:
        """Creates a new sticker set.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
               Unique identifier (int) or username (str) of sticker file owner.

            name (``str``):
                Short name of the sticker set, to be used in t.me/addstickers/ URLs (e.g., *animals*).
                Can contain only English letters, digits and underscores.
                Must end with *"_by_<bot username>"* (*<bot_username>* is case insensitive) for bots, 0-64 characters.

            title (``str``):
                Sticker set title, 1-64 characters.

            stickers (List of :obj:`~pyrogram.types.InputSticker`):
                List of stickers to be added to the set, must be up to 200 stickers.

            sticker_type (:obj:`~pyrogram.enums.StickerType`, *optional*):
                Type of stickers in the set, pass :obj:`~pyrogram.enums.StickerType.REGULAR`, :obj:`~pyrogram.enums.StickerType.MASK`, or :obj:`~pyrogram.enums.StickerType.CUSTOM_EMOJI`.
                By default, a regular sticker set is created.

            needs_repainting (``bool``, *optional*):
                Pass *True* if stickers in the sticker set must be repainted to the color of text when used in messages,
                the accent color if used as emoji status, white on chat photos, or another appropriate color based on context.
                For custom emoji sticker sets only.

        Returns:
            :obj:`~pyrogram.types.StickerSet`: A created sticker set is returned.

        Example:
            .. code-block:: python

                from pyrogram import enums

                await app.create_new_sticker_set(
                    "me",
                    "my_sticker_set",
                    "New title",
                    stickers=[
                        types.InputSticker(
                            sticker="sticker.png",
                            format=enums.StickerFormat.STATIC,
                            emoji_list=["👍"]
                        )
                    ]
                )
        """
        r = await self.invoke(
            raw.functions.stickers.CreateStickerSet(
                user_id=await self.resolve_peer(user_id),
                title=title,
                short_name=name,
                stickers=[
                    await sticker.write(client=self, chat_id=user_id) for sticker in stickers
                ],
                masks=sticker_type == enums.StickerType.MASK,
                emojis=sticker_type == enums.StickerType.CUSTOM_EMOJI,
                text_color=needs_repainting,
            )
        )

        return await types.StickerSet._parse(self, r)

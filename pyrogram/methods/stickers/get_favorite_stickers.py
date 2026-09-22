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


class GetFavoriteStickers:
    async def get_favorite_stickers(self: pyrogram.Client) -> list[types.Sticker]:
        """Returns a list of favorite stickers.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            List of :obj:`~pyrogram.types.Sticker`: On success, a list of sticker objects is returned.
        """
        r = await self.invoke(raw.functions.messages.GetFavedStickers(hash=0))

        return types.List(
            [
                await types.Sticker._parse(
                    client=self,
                    sticker=sticker,
                    document_attributes={type(i): i for i in sticker.attributes},
                )
                for sticker in r.stickers
            ]
        )

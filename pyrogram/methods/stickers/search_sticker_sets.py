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


class SearchStickerSets:
    async def search_sticker_sets(
        self: pyrogram.Client, sticker_type: enums.StickerType, query: str
    ) -> list[types.StickerSet]:
        """Searches for sticker sets by looking for specified query in their title and name.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            sticker_type (:obj:`~pyrogram.enums.StickerType`):
                Type of the sticker sets to return.

            query (``str``):
                Query to search for.

        Returns:
            List of :obj:`~pyrogram.types.StickerSet`: A list of sticker sets that match the query is returned.
        """
        r = await self.invoke(raw.functions.messages.SearchStickerSets(q=query, hash=0))

        sticker_sets = types.List()

        for sticker_set in r.sets:
            parsed = await types.StickerSet._parse(self, sticker_set.set)

            if parsed.sticker_type == sticker_type:
                sticker_sets.append(parsed)

        return sticker_sets

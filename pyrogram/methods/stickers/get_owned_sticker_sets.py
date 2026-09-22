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

from collections.abc import AsyncGenerator

import pyrogram
from pyrogram import raw, types


class GetOwnedStickerSets:
    async def get_owned_sticker_sets(
        self: pyrogram.Client, limit: int = 0, offset_sticker_set_id: int = 0
    ) -> AsyncGenerator[types.StickerSet, None]:
        """Returns sticker sets owned by the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            limit (``int``):
                Limits the number of sticker sets to be retrieved.
                By default, no limit is applied and all sets are returned.

            offset_sticker_set_id (``int``):
                Identifier of the sticker set from which to return owned sticker sets.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.StickerSet` objects.
        """
        current = 0
        total = limit or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.messages.GetMyStickers(offset_id=offset_sticker_set_id, limit=limit)
            )

            sticker_sets: list[types.StickerSet] = types.List(
                [await types.StickerSet._parse(self, sticker_set.set) for sticker_set in r.sets]
            )

            if not sticker_sets:
                return

            offset_sticker_set_id = sticker_sets[-1].id

            for sticker_set in sticker_sets:
                yield sticker_set

                current += 1

                if current >= total:
                    return

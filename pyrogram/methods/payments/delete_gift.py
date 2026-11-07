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


class DeleteGift:
    async def delete_gift(
        self: pyrogram.Client, owned_gift_id: str, business_connection_id: str | None = None
    ) -> bool:
        """Deletes a gift without receiving Telegram Stars for it.

        .. note::

            Only unlimited gifts can be deleted.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            owned_gift_id (``str``):
                Unique identifier of the regular gift that should be deleted.

            business_connection_id (``str``, *optional*):
                Unique identifier of business connection on behalf of which to send the request.
                For bots only.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Delete gift
                await app.delete_gift(owned_gift_id="123456")
        """
        r = await self.invoke(
            raw.functions.payments.DeleteStarGift(
                stargift=await utils.get_input_stargift(self, owned_gift_id)
            ),
            business_connection_id=business_connection_id,
        )

        return r

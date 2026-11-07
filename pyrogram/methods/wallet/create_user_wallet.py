#  Kurigram - Telegram MTProto API Client Library for Python
#
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present KurimuzonAkuma <https://github.com/KurimuzonAkuma>
#
#  This file is part of Kurigram.
#
#  Kurigram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Kurigram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Kurigram. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations


import pyrogram
from pyrogram import raw, types


class CreateUserWallet:
    async def create_user_wallet(
        self: pyrogram.Client, user_id: int | str
    ) -> types.UserTonWalletAddress | None:
        """Creates a TON wallet for the specified regular user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            :obj:`~pyrogram.types.UserTonWalletAddress` | None: On success, information about created user wallet address is returned.
        """
        r = await self.invoke(
            raw.functions.wallet.GetUserAddresses(
                force=True, id=[await self.resolve_peer(user_id)], addresses=[]
            )
        )

        if not r.addresses:
            return None

        users = {i.id: i for i in r.users}

        return await types.UserTonWalletAddress._parse(self, r.addresses[0], users)

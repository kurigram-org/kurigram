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

import asyncio

import pyrogram
from pyrogram import raw, types


class GetUserTonWalletAddresses:
    async def get_user_ton_wallet_addresses(
        self: pyrogram.Client,
        user_ids: int | str | list[int | str],
    ) -> list[types.UserTonWalletAddress]:
        """Returns TON wallet addresses of the specified users.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            user_ids (``int`` | ``str`` | List of ``int`` | ``str``):
                User identifiers (int) or usernames (str) of the users whose wallet addresses have to be returned.
                If a user has no TON wallet, it will be skipped in the result.

        Returns:
            List of :obj:`~pyrogram.types.UserTonWalletAddress`: The TON wallet addresses of the specified users.
        """
        is_iterable = not isinstance(user_ids, (int, str))
        user_ids = list(user_ids) if is_iterable else [user_ids]
        user_ids = await asyncio.gather(*[self.resolve_peer(i) for i in user_ids])

        r = await self.invoke(raw.functions.wallet.GetUserAddresses(id=user_ids, addresses=[]))

        users = {i.id: i for i in r.users}

        return types.List(
            [
                await types.UserTonWalletAddress._parse(self, address, users)
                for address in r.addresses
            ]
        )

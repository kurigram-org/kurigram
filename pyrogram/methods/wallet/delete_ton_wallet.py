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
from pyrogram import raw, utils, types


class DeleteTonWallet:
    async def delete_ton_wallet(
        self: pyrogram.Client, password: str | None = None
    ) -> types.TonWalletState:
        """Deletes the current TON wallet of the user and creates a new one.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            password (``int`` | ``str``, *optional*):
                Password of the current user.

        Returns:
            :obj:`~pyrogram.types.TonWalletState`: On success, the new state of the TON wallet is returned.
        """
        r = await self.invoke(
            raw.functions.wallet.ReplaceWallet(
                wallet=raw.types.InputWalletNew(),
                password=utils.compute_password_check(
                    await self.invoke(raw.functions.account.GetPassword()), password
                )
                if password is not None
                else None,
            )
        )

        return await types.TonWalletState._parse(r)

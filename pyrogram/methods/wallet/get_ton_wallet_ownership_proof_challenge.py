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


class GetTonWalletOwnershipProofChallenge:
    async def get_ton_wallet_ownership_proof_challenge(
        self: pyrogram.Client,
    ) -> types.TonWalletOwnershipProofChallenge:
        """Returns a challenge which may be used to proof ownership of a TON wallet.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            :obj:`~pyrogram.types.TonWalletOwnershipProofChallenge`: The challenge for proving ownership of a TON wallet.
        """
        r = await self.invoke(raw.functions.wallet.GetProofChallenge())

        return await types.TonWalletOwnershipProofChallenge._parse(r)

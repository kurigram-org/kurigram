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


class ReplaceTonWallet:
    async def replace_ton_wallet(
        self: pyrogram.Client,
        proof: types.TonWalletOwnershipProof,
        password: str | None = None,
        anchor_public_key: bytes | None = None,
    ) -> types.TonWalletState:
        """Replaces the current TON wallet with another existing v6r2 wallet or changes private key of the current TON wallet.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            proof (:obj:`~pyrogram.types.TonWalletOwnershipProof`):
                Proof of ownership of the new private key of the TON wallet.
                Use :meth:`~pyrogram.Client.get_ton_wallet_ownership_proof_challenge` to get a challenge for the proof.

            password (``int`` | ``str``, *optional*):
                Password of the current user.

            anchor_public_key (``bytes``, *optional*):
                Original public key of the new TON wallet.

        Returns:
            :obj:`~pyrogram.types.TonWalletState`: On success, the new state of the TON wallet is returned.
        """
        r = await self.invoke(
            raw.functions.wallet.ReplaceWallet(
                wallet=raw.types.InputWalletImported(
                    public_key=proof.public_key,
                    proof=raw.types.WalletOwnershipProof(
                        timestamp=proof.timestamp, signature=proof.signature
                    ),
                    anchor_public_key=anchor_public_key,
                ),
                password=utils.compute_password_check(
                    await self.invoke(raw.functions.account.GetPassword()), password
                )
                if password is not None
                else None,
            )
        )

        return await types.TonWalletState._parse(r)

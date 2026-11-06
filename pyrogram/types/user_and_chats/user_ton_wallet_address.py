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

from ..object import Object


class UserTonWalletAddress(Object):
    """Contains TON wallet address of a user.

    Parameters:
        wallet_address (``str``):
            Address of the user's wallet in the TON blockchain.

        public_key (``bytes``):
            Public key of the user.

        user (:obj:`~pyrogram.types.User`, *optional*):
            The user to whom the wallet belongs.
    """

    def __init__(self, *, wallet_address: str, public_key: bytes, user: types.User | None = None):
        super().__init__()

        self.wallet_address = wallet_address
        self.public_key = public_key
        self.user = user

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        address: raw.types.WalletUserAddress,
        users: dict[int, raw.base.User],
    ) -> UserTonWalletAddress:
        raw_user = users.get(address.user_id)

        return UserTonWalletAddress(
            wallet_address=address.address,
            public_key=address.public_key,
            user=await types.User._parse(client, raw_user) if raw_user is not None else None,
        )

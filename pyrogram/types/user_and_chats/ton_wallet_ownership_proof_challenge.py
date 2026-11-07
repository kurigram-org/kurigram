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

from typing import TYPE_CHECKING

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import raw


class TonWalletOwnershipProofChallenge(Object):
    """Represents a challenge for TON wallet ownership proof.

    Parameters:
        payload (``str``):
            Payload of the challenge.

        domain (``str``):
            Domain of the proof requester.
    """

    def __init__(self, *, payload: str, domain: str):
        super().__init__()

        self.payload = payload
        self.domain = domain

    @staticmethod
    async def _parse(
        challenge: raw.types.wallet.ProofChallenge,
    ) -> TonWalletOwnershipProofChallenge:
        return TonWalletOwnershipProofChallenge(
            payload=challenge.payload,
            domain=challenge.domain,
        )

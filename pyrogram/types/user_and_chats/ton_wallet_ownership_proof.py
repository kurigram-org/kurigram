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

from ..object import Object


class TonWalletOwnershipProof(Object):
    """Represents a proof of TON wallet ownership.

    Parameters:
        public_key (``bytes``):
            Public key of the wallet.

        timestamp (``int``):
            The current UNIX timestamp which was used to create the proof.

        signature (``bytes``):
            The signature prooving the ownership.
    """

    def __init__(self, *, public_key: bytes, timestamp: int, signature: bytes):
        super().__init__()

        self.public_key = public_key
        self.timestamp = timestamp
        self.signature = signature

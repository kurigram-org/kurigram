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


class TonNftAttribute(Object):
    """This object represents an attribute of an NFT in the TON blockchain.

    Parameters:
        trait_type (``str``):
            Trait type of the attribute.

        value (``str``):
            Value of the attribute.
    """

    def __init__(
        self,
        *,
        trait_type: str,
        value: str,
    ) -> None:
        super().__init__()

        self.trait_type = trait_type
        self.value = value

    @staticmethod
    def _parse(attribute: raw.types.wallet.NftAttribute) -> TonNftAttribute:
        return TonNftAttribute(trait_type=attribute.trait_type, value=attribute.value)

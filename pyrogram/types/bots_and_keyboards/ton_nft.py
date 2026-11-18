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

from pyrogram import types

from ..object import Object

if TYPE_CHECKING:
    import pyrogram
    from pyrogram import raw


class TonNft(Object):
    """This object represents an NFT in the TON blockchain.

    Parameters:
        address (``str``):
            Address of the NFT.

        collection_address (``str``, *optional*):
            Address of the collection to which the NFT belongs. Omitted if unknown.

        index (``str``):
            Index of the NFT among all NFTs from the collection as a decimal number.

        name (``str``, *optional*):
            Name of the NFT.

        description (``str``, *optional*):
            Description of the NFT.

        attributes (List of :obj:`~pyrogram.types.TonNftAttribute`, *optional*):
            Attributes of the NFT.

        gift (:obj:`~pyrogram.types.Gift`, *optional*):
            The unique gift corresponding to the NFT.
    """

    def __init__(
        self,
        *,
        address: str,
        collection_address: str | None = None,
        index: str,
        name: str | None = None,
        description: str | None = None,
        attributes: list[types.TonNftAttribute] | None = None,
        gift: types.Gift | None = None,
    ) -> None:
        super().__init__()

        self.address = address
        self.collection_address = collection_address
        self.index = index
        self.name = name
        self.description = description
        self.attributes = attributes
        self.gift = gift

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        nft: raw.types.wallet.NftItem,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> TonNft:
        return TonNft(
            address=nft.address,
            collection_address=nft.collection_address,
            index=nft.index,
            name=nft.name,
            description=nft.description,
            attributes=types.List(
                [types.TonNftAttribute._parse(attribute) for attribute in nft.attributes]
            )
            if nft.attributes is not None
            else None,
            gift=await types.Gift._parse(client, nft.gift, users=users, chats=chats)
            if nft.gift
            else None,
        )

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


class TonWalletCard(Object):
    """This object describes a TON wallet card, which is shown on the profile page of a user to everyone.

    Parameters:
        address (``str``):
            Address of the wallet.

        amount (``str``):
            Balance of the wallet, in the smallest units of the cryptocurrency, as a decimal number.

        stickers (List of :obj:`~pyrogram.types.TonWalletCardSticker`):
            Stickers placed on the card.

        background_nft_address (``str``, *optional*):
            Address of the NFT of one of the stickers, whose colors must be used for the card background.
            Omitted if the default background must be used.
    """

    def __init__(
        self,
        *,
        address: str,
        amount: str,
        stickers: list[types.TonWalletCardSticker],
        background_nft_address: str | None = None,
    ) -> None:
        super().__init__()

        self.address = address
        self.amount = amount
        self.stickers = stickers
        self.background_nft_address = background_nft_address

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        card: raw.types.wallet.Card,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> TonWalletCard:
        return TonWalletCard(
            address=card.address,
            amount=str(card.balance),
            stickers=types.List(
                [
                    await types.TonWalletCardSticker._parse(client, sticker, users, chats)
                    for sticker in card.stickers or []
                ]
            ),
            background_nft_address=card.bg_nft_item.address if card.bg_nft_item else None,
        )

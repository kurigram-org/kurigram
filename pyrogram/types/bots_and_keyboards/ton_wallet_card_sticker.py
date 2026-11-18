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


class TonWalletCardSticker(Object):
    """This object describes a sticker on a TON wallet card.

    Parameters:
        position (:obj:`~pyrogram.types.AreaPosition`):
            Position of the sticker on the card.

        nft (:obj:`~pyrogram.types.TonNft`):
            The NFT shown as the sticker.
    """

    def __init__(
        self,
        *,
        position: types.AreaPosition,
        nft: types.TonNft,
    ) -> None:
        super().__init__()

        self.position = position
        self.nft = nft

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        sticker: raw.types.wallet.CardSticker,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> TonWalletCardSticker:
        return TonWalletCardSticker(
            position=types.AreaPosition._parse(sticker.coordinates),
            nft=await types.TonNft._parse(client, sticker.nft, users, chats),
        )

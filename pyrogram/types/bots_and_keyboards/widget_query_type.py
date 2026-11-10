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

from base64 import b64encode

import pyrogram
from pyrogram import raw, types

from ..object import Object


class WidgetQueryType(Object):
    """This object describes the type of a query from a widget.

    It can be one of:

    - :obj:`~pyrogram.types.WidgetQueryTypeData`
    - :obj:`~pyrogram.types.WidgetQueryTypeSignData`
    - :obj:`~pyrogram.types.WidgetQueryTypeSentTransaction`
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        query_type: raw.base.WidgetQueryType,
        wallet_card: raw.base.wallet.Card | None,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> WidgetQueryType:
        if isinstance(query_type, raw.types.WidgetQueryTypeData):
            return WidgetQueryTypeData(
                wallet_card=await types.TonWalletCard._parse(client, wallet_card, users, chats)
                if query_type.with_wallet and wallet_card is not None
                else None,
            )
        if isinstance(query_type, raw.types.WidgetQueryTypeSignData):
            return WidgetQueryTypeSignData(
                wallet=WidgetQueryWallet._parse(query_type.wallet),
                sign_data=query_type.sign_data.data,
            )
        return WidgetQueryTypeSentTransaction(
            wallet=WidgetQueryWallet._parse(query_type.wallet),
            msg_hash=query_type.msg_hash,
        )


class WidgetQueryTypeData(WidgetQueryType):
    """The query contains data for the bot.

    Parameters:
        wallet_card (:obj:`~pyrogram.types.TonWalletCard`, *optional*):
            TON wallet card of the user who sent the query, if it was sent to the bot along with the query.
    """

    def __init__(self, *, wallet_card: types.TonWalletCard | None = None) -> None:
        super().__init__()

        self.wallet_card = wallet_card


class WidgetQueryTypeSignData(WidgetQueryType):
    """The query contains data signed by a TON wallet of the user who sent the query.

    The data is signed for the domain ``bot<bot_id>``, where ``<bot_id>`` is the identifier of the bot.

    Parameters:
        wallet (:obj:`~pyrogram.types.WidgetQueryWallet`):
            The wallet that signed the data.

        sign_data (``str``):
            JSON-serialized signed data.
    """

    def __init__(self, *, wallet: WidgetQueryWallet, sign_data: str) -> None:
        super().__init__()

        self.wallet = wallet
        self.sign_data = sign_data


class WidgetQueryTypeSentTransaction(WidgetQueryType):
    """The query notifies the bot about a transaction sent from a TON wallet of the user who sent the query.

    Parameters:
        wallet (:obj:`~pyrogram.types.WidgetQueryWallet`):
            The wallet from which the transaction was sent.

        msg_hash (``str``):
            Value of ``msg_hash`` of the transaction.
    """

    def __init__(self, *, wallet: WidgetQueryWallet, msg_hash: str) -> None:
        super().__init__()

        self.wallet = wallet
        self.msg_hash = msg_hash


class WidgetQueryWallet(Object):
    """This object describes a TON wallet of the user, which is used in a query from a widget.

    Parameters:
        address (``str``):
            Address of the wallet.

        amount (``str``):
            Balance of the wallet, in the smallest units of the cryptocurrency, as a decimal number.

        public_key (``str``, *optional*):
            Hex-encoded public key of the wallet. Omitted if unknown.

        state_init (``str``, *optional*):
            Base64-encoded serialized StateInit of the wallet contract.
            Omitted if and only if *public_key* is omitted.
    """

    def __init__(
        self,
        *,
        address: str,
        amount: str,
        public_key: str | None = None,
        state_init: str | None = None,
    ) -> None:
        super().__init__()

        self.address = address
        self.amount = amount
        self.public_key = public_key
        self.state_init = state_init

    @staticmethod
    def _parse(wallet: raw.types.UserWallet) -> WidgetQueryWallet:
        return WidgetQueryWallet(
            address=wallet.address,
            amount=str(wallet.balance),
            public_key=wallet.public_key.hex() if wallet.public_key else None,
            state_init=b64encode(wallet.state_init).decode() if wallet.state_init else None,
        )

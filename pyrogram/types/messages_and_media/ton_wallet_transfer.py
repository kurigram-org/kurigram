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


class TonWalletTransfer(Object):
    """Represents a transfer with the TON wallet of the current user.

    Parameters:
        sender (:obj:`~pyrogram.types.User`):
            Sender of the transfer.

        transaction_id (``str``):
            Unique identifier of the transaction.

        peer_address (``str``):
            Address in the TON blockchain of the transaction peer.

        amount (``int``):
            The amount of received cryptocurrency, in the smallest units of the cryptocurrency.

        comment (``str``, *optional*):
            Comment added to the transaction.

        is_comment_encrypted (``bool``, *optional*):
            True, if the comment is encrypted and must be decrypted using the receiver's or sender's private key.
    """

    def __init__(
        self,
        *,
        sender: types.User,
        transaction_id: str,
        peer_address: str,
        amount: int,
        comment: str | None = None,
        is_comment_encrypted: bool | None = None,
    ):
        super().__init__()

        self.sender = sender
        self.transaction_id = transaction_id
        self.peer_address = peer_address
        self.amount = amount
        self.comment = comment
        self.is_comment_encrypted = is_comment_encrypted

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        action: raw.types.MessageActionGramTransfer,
        sender_id: int,
        users: dict[int, raw.base.User],
    ) -> TonWalletTransfer:
        return TonWalletTransfer(
            sender=await types.User._parse(client, users.get(sender_id)),
            transaction_id=action.transaction_id,
            peer_address=action.peer_address,
            amount=action.amount,
            comment=action.comment,
            is_comment_encrypted=action.comment_encrypted,
        )

    @property
    def link(self) -> str:
        """Returns a link to view the transaction in a TON blockchain explorer."""
        return f"https://tonviewer.com/transaction/{self.transaction_id}"

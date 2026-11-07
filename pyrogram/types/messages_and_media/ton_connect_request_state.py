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

from pyrogram import raw, utils

from ..object import Object

if TYPE_CHECKING:
    import datetime


class TonConnectRequestState(Object):
    """Describes state of a request received from a dApp through TON Connect.

    It can be one of:

    - :obj:`~pyrogram.types.TonConnectRequestStatePending`
    - :obj:`~pyrogram.types.TonConnectRequestStateAccepted`
    - :obj:`~pyrogram.types.TonConnectRequestStateRejected`
    """

    def __init__(self) -> None:
        super().__init__()

    async def _parse(
        action: raw.types.MessageActionWalletTonConnectRequest,
    ) -> TonConnectRequestState:
        if action.accepted:
            return TonConnectRequestStateAccepted()

        if action.rejected:
            return TonConnectRequestStateRejected()

        return TonConnectRequestStatePending(
            expiration_date=utils.timestamp_to_datetime(action.expires)
        )


class TonConnectRequestStatePending(TonConnectRequestState):
    """The request must be accepted or rejected if it isn't expired yet.

    Parameters:
        expiration_date (:obj:`datetime.datetime`):
            The date when the request will expire or has expired.
    """

    def __init__(
        self,
        expiration_date: datetime.datetime,
    ) -> None:
        super().__init__()

        self.expiration_date = expiration_date


class TonConnectRequestStateAccepted(TonConnectRequestState):
    """The request was accepted."""

    def __init__(
        self,
    ) -> None:
        super().__init__()


class TonConnectRequestStateRejected(TonConnectRequestState):
    """The request was rejected."""

    def __init__(
        self,
    ) -> None:
        super().__init__()

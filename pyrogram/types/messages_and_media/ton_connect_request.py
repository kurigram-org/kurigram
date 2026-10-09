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

from pyrogram import raw, types

from ..object import Object


class TonConnectRequest(Object):
    """A request from a dApp was received through TON Connect.

    Parameters:
        session_id (``int``):
            Unique identifier of the TON Connect session.

        state (:obj:`~pyrogram.types.TonConnectRequestState`):
            State of the request.

        dapp_name (``str``, *optional*):
            Name of the dApp.

        topic (``str``, *optional*):
            Topic of the request.

        trace_id (``str``, *optional*):
            Identifier to trace the request.
    """

    def __init__(
        self,
        *,
        session_id: int,
        state: types.TonConnectRequestState,
        dapp_name: str | None = None,
        topic: str | None = None,
        trace_id: str | None = None,
    ):
        super().__init__()

        self.session_id = session_id
        self.state = state
        self.dapp_name = dapp_name
        self.topic = topic
        self.trace_id = trace_id

    @staticmethod
    async def _parse(
        action: raw.types.MessageActionWalletTonConnectRequest,
    ) -> TonConnectRequest:
        return TonConnectRequest(
            session_id=action.session_id,
            state=types.TonConnectRequestState._parse(action),
            dapp_name=action.dapp_name,
            topic=action.topic,
            trace_id=action.trace_id,
        )

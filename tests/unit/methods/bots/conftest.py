#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import annotations as _annotations

import base64
import struct
from typing import Final

from pyrogram import raw
from pyrogram.methods.bots.get_game_high_scores import GetGameHighScores
from pyrogram.methods.bots.set_game_score import SetGameScore

INLINE_MESSAGE_DC_ID: Final[int] = 4

# The Bot API packs `inline_message_id` as unpadded url-safe base64 of `<iqq`: DC, message id,
#  access hash. Packed here from that layout rather than by the code under test.
INLINE_MESSAGE_ID: Final[str] = (
    base64.urlsafe_b64encode(struct.pack("<iqq", INLINE_MESSAGE_DC_ID, 42, 7)).decode().rstrip("=")
)

RAW_INLINE_MESSAGE_ID: Final[raw.types.InputBotInlineMessageID] = raw.types.InputBotInlineMessageID(
    dc_id=INLINE_MESSAGE_DC_ID,
    id=42,
    access_hash=7,
)

# Not the `Session.SLEEP_THRESHOLD` default, so a query sent without the client's own value shows.
CLIENT_SLEEP_THRESHOLD: Final[float] = 42


class FakeSession:
    """Records the wire bytes and flood wait threshold of every query sent through it.

    Bytes, because `TLObject.__eq__` never compares the type: `InputUserSelf() == InputUser(user_id=7,
    access_hash=0)` is `True`, so a query-to-query assert passes with the user dropped.
    """

    def __init__(self, response: raw.core.TLObject | bool) -> None:
        self._response = response
        self._sent: list[tuple[bytes, float | None]] = []

    @property
    def sent(self) -> list[tuple[bytes, float | None]]:
        return self._sent

    async def invoke(
        self,
        query: raw.core.TLObject,
        sleep_threshold: float | None = None,
    ) -> raw.core.TLObject | bool:
        self._sent.append((query.write(), sleep_threshold))

        return self._response


class GameClient(SetGameScore, GetGameHighScores):
    """A client whose sessions are one `FakeSession`, recording which sessions were asked for.

    `invoke` stands for the main session and goes through the same `FakeSession`.
    """

    sleep_threshold: float = CLIENT_SLEEP_THRESHOLD

    def __init__(self, response: raw.core.TLObject | bool) -> None:
        self._session = FakeSession(response)
        self._requested_sessions: list[tuple[int, bool]] = []

    @property
    def session(self) -> FakeSession:
        return self._session

    @property
    def requested_sessions(self) -> list[tuple[int, bool]]:
        return self._requested_sessions

    async def get_session(self, dc_id: int, *, is_media: bool) -> FakeSession:
        self._requested_sessions.append((dc_id, is_media))

        return self._session

    async def invoke(self, query: raw.core.TLObject) -> raw.core.TLObject | bool:
        return await self._session.invoke(query)

    async def resolve_peer(self, peer_id: int | str) -> raw.types.InputUser:
        return raw.types.InputUser(
            user_id=int(peer_id),
            access_hash=0,
        )

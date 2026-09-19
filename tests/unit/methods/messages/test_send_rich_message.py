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

from typing import Final, TYPE_CHECKING

import pytest

from pyrogram import raw, types
from pyrogram.methods.messages.send_rich_message import SendRichMessage

if TYPE_CHECKING:
    from pyrogram.raw.core import TLObject

_BUSINESS_CONNECTION_ID: Final[str] = "connection-id"


class FakeClient(SendRichMessage):
    """A client that records the query and the business connection handed to `invoke`."""

    def __init__(self) -> None:
        self.captured_query: TLObject | None = None
        self.captured_business_connection_id: str | None = None

    def rnd_id(self) -> int:
        return 1

    async def resolve_peer(self, peer_id: int | str) -> raw.base.InputPeer:
        return raw.types.InputPeerUser(
            user_id=int(peer_id),
            access_hash=0,
        )

    async def invoke(
        self,
        query: TLObject,
        business_connection_id: str | None = None,
    ) -> raw.base.messages.Messages:
        self.captured_query = query
        self.captured_business_connection_id = business_connection_id

        return raw.types.messages.Messages(
            messages=[],
            chats=[],
            users=[],
            topics=[],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("ephemeral_message_parameters", "expected_query"),
    [
        pytest.param(None, raw.functions.messages.SendMessage, id="plain"),
        pytest.param(
            types.EphemeralMessageParameters(receiver_user_id=8),
            raw.functions.ephemeral.SendMessage,
            id="ephemeral",
        ),
    ],
)
async def test_the_business_connection_reaches_invoke_on_either_branch(
    *,
    ephemeral_message_parameters: types.EphemeralMessageParameters | None,
    expected_query: type[TLObject],
) -> None:
    # The method builds two different RPCs and invokes both from one call site, so the
    #  connection has to survive whichever branch built the query.
    client = FakeClient()

    await client.send_rich_message(
        chat_id=7,
        rich_message=types.InputRichMessage(html="Hello <b>World</b>"),
        ephemeral_message_parameters=ephemeral_message_parameters,
        business_connection_id=_BUSINESS_CONNECTION_ID,
    )

    assert isinstance(client.captured_query, expected_query)
    assert client.captured_business_connection_id == _BUSINESS_CONNECTION_ID


@pytest.mark.asyncio
async def test_a_send_without_a_business_connection_invokes_on_the_ordinary_session() -> None:
    client = FakeClient()

    await client.send_rich_message(
        chat_id=7,
        rich_message=types.InputRichMessage(html="Hello <b>World</b>"),
    )

    assert client.captured_business_connection_id is None

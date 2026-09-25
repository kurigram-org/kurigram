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

import datetime as dt

import pytest

from pyrogram import raw, types
from pyrogram.methods.messages.send_message import SendMessage
from pyrogram.parser import Parser


class FakeClient(SendMessage):
    """A client that records the query built for `messages.SendMessage`, sending nothing."""

    def __init__(self) -> None:
        self.parser = Parser(None)
        self.link_preview_options: types.LinkPreviewOptions | None = None
        self.captured: raw.functions.messages.SendMessage | None = None

    def rnd_id(self) -> int:
        return 1

    async def resolve_peer(self, peer_id: int | str) -> raw.base.InputPeer:
        return raw.types.InputPeerUser(
            user_id=int(peer_id),
            access_hash=0,
        )

    async def invoke(
        self,
        query: raw.functions.messages.SendMessage,
        *,
        business_connection_id: str | None = None,
    ) -> raw.base.messages.Messages:
        self.captured = query

        return raw.types.messages.Messages(
            messages=[],
            chats=[],
            users=[],
            topics=[],
        )


@pytest.mark.asyncio
async def test_timedelta_schedule_date_is_sent_as_a_timestamp_from_now() -> None:
    client = FakeClient()
    delay = dt.timedelta(hours=1)

    earliest = int((dt.datetime.now() + delay).timestamp())
    await client.send_message(
        chat_id=7,
        text="later",
        schedule_date=delay,
    )
    latest = int((dt.datetime.now() + delay).timestamp())

    assert client.captured is not None

    schedule_date = client.captured.schedule_date
    assert schedule_date is not None
    assert earliest <= schedule_date <= latest

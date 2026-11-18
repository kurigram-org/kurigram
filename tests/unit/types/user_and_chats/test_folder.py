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

import pytest

import pyrogram
from pyrogram import raw, types


@pytest.mark.asyncio
async def test_a_folder_holding_self_keeps_an_empty_slot_for_it() -> None:
    folder = raw.types.DialogFilter(
        id=2,
        title=raw.types.TextWithEntities(
            text="Folder",
            entities=[],
        ),
        pinned_peers=[],
        include_peers=[raw.types.InputPeerSelf()],
        exclude_peers=[],
    )
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    parsed = await types.Folder._parse(client, folder, {}, {})

    assert parsed.included_chats == [None]


@pytest.mark.asyncio
async def test_a_folder_holding_an_empty_user_or_chat_keeps_an_empty_slot_for_it() -> None:
    folder = raw.types.DialogFilter(
        id=2,
        title=raw.types.TextWithEntities(
            text="Folder",
            entities=[],
        ),
        pinned_peers=[],
        include_peers=[
            raw.types.InputPeerUser(
                user_id=3,
                access_hash=0,
            ),
            raw.types.InputPeerChat(chat_id=4),
        ],
        exclude_peers=[],
    )
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    parsed = await types.Folder._parse(
        client,
        folder,
        {3: raw.types.UserEmpty(id=3)},
        {4: raw.types.ChatEmpty(id=4)},
    )

    assert parsed.included_chats == [None, None]

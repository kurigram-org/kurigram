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
from typing import Final

import pytest

from pyrogram import enums, raw, types

# `utils.get_channel_id(1)`: channel-space ids are the raw id below `-10**12`.
_COMMUNITY_CHAT_ID: Final[int] = -1000000000001

_COMMUNITY: Final[raw.types.Community] = raw.types.Community(
    id=1,
    title="Community",
    photo=raw.types.ChatPhoto(
        photo_id=5,
        dc_id=2,
    ),
    date=1_700_000_000,
    access_hash=2,
    creator=True,
    min=False,
    admin_rights=raw.types.ChatAdminRights(change_info=True),
)
# File ids of the photo above, as `types.ChatPhoto._parse` encodes them for this community.
_PARSED_PHOTO: Final[types.ChatPhoto] = types.ChatPhoto(
    small_file_id="AQADAgADBQAXAgAD_-9aKxf___8CAAseBA",
    small_photo_unique_id="AgADBQAH",
    big_file_id="AQADAgADBQAXAwAD_-9aKxf___8CAAseBA",
    big_photo_unique_id="AgADBQAH",
)
_PARSED_COMMUNITY: Final[types.Community] = types.Community(
    id=_COMMUNITY_CHAT_ID,
    have_access=True,
    name="Community",
    photo=_PARSED_PHOTO,
    date=dt.datetime.fromtimestamp(1_700_000_000),
    status=types.CommunityMemberStatusCreator(),
    raw=_COMMUNITY,
)

_COMMUNITY_FORBIDDEN: Final[raw.types.CommunityForbidden] = raw.types.CommunityForbidden(
    id=1,
    title="Community",
)


# Both used to raise `AttributeError: 'Community' object has no attribute 'monoforum'`.
@pytest.mark.parametrize(
    ("community", "expected"),
    [
        pytest.param(
            _COMMUNITY,
            types.Chat(
                id=_COMMUNITY_CHAT_ID,
                type=enums.ChatType.COMMUNITY,
                is_min=False,
                is_creator=True,
                is_admin=True,
                title="Community",
                photo=_PARSED_PHOTO,
                dc_id=2,
                community_id=_COMMUNITY_CHAT_ID,
                community=_PARSED_COMMUNITY,
                raw=_COMMUNITY,
            ),
            id="community",
        ),
        pytest.param(
            _COMMUNITY_FORBIDDEN,
            types.Chat(
                id=_COMMUNITY_CHAT_ID,
                type=enums.ChatType.COMMUNITY,
                title="Community",
                is_banned=True,
                community_id=_COMMUNITY_CHAT_ID,
                community=types.Community(
                    id=_COMMUNITY_CHAT_ID,
                    have_access=False,
                    name="Community",
                    raw=_COMMUNITY_FORBIDDEN,
                ),
                raw=_COMMUNITY_FORBIDDEN,
            ),
            id="community-forbidden",
        ),
    ],
)
@pytest.mark.asyncio
async def test_a_community_dialog_parses_as_a_community_chat(
    community: raw.types.Community | raw.types.CommunityForbidden,
    *,
    expected: types.Chat,
) -> None:
    parsed = await types.Chat._parse_dialog(
        None,
        raw.types.PeerChannel(channel_id=1),
        {},
        {1: community},
    )

    assert parsed == expected


# `_parse_full` matched no branch for `CommunityFull`, so `get_chat` returned `None`.
@pytest.mark.asyncio
async def test_a_full_community_parses_as_a_community_chat() -> None:
    community_full = raw.types.CommunityFull(
        id=1,
        about="About",
        chat_photo=raw.types.PhotoEmpty(id=0),
        linked_peers=[],
        admins_count=3,
        kicked_count=4,
    )

    parsed = await types.Chat._parse_full(
        None,
        raw.types.messages.ChatFull(
            full_chat=community_full,
            chats=[_COMMUNITY],
            users=[],
        ),
    )

    assert parsed == types.Chat(
        id=_COMMUNITY_CHAT_ID,
        type=enums.ChatType.COMMUNITY,
        is_min=False,
        is_creator=True,
        is_admin=True,
        title="Community",
        photo=_PARSED_PHOTO,
        dc_id=2,
        description="About",
        admins_count=3,
        kicked_count=4,
        community_id=_COMMUNITY_CHAT_ID,
        community=_PARSED_COMMUNITY,
        raw=community_full,
    )


# Both used to reach the channel parser, which raised `AttributeError: 'ChatEmpty' object has no
#  attribute 'monoforum'` (`'UserEmpty'` for the other), so `get_chat(force_full=False)` crashed
#  on a peer the account can no longer see instead of returning `None`.
@pytest.mark.parametrize(
    "empty",
    [
        pytest.param(raw.types.ChatEmpty(id=1), id="chat-empty"),
        pytest.param(raw.types.UserEmpty(id=1), id="user-empty"),
    ],
)
@pytest.mark.asyncio
async def test_an_empty_peer_parses_as_none(
    empty: raw.types.ChatEmpty | raw.types.UserEmpty,
) -> None:
    assert await types.Chat._parse_chat(None, empty) is None

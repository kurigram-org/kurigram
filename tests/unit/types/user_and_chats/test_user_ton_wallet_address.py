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

from typing import Final

import pytest

import pyrogram
from pyrogram import raw, types


_USER_ID: Final[int] = 7


@pytest.mark.parametrize(
    ("users", "expected"),
    [
        pytest.param({}, None, id="missing"),
        pytest.param(
            {
                _USER_ID: raw.types.User(
                    id=_USER_ID,
                    first_name="Owner",
                ),
            },
            _USER_ID,
            id="known",
        ),
    ],
)
@pytest.mark.asyncio
async def test_an_address_names_its_user_only_when_users_has_it(
    users: dict[int, raw.base.User],
    *,
    expected: int | None,
) -> None:
    address = raw.types.WalletUserAddress(
        address="address",
        public_key=b"key",
        user_id=_USER_ID,
    )
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    parsed = await types.UserTonWalletAddress._parse(client, address, users)

    assert getattr(parsed.user, "id", None) == expected

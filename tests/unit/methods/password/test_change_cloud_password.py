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

from pyrogram import raw
from pyrogram.methods.password.change_cloud_password import ChangeCloudPassword
from pyrogram.utils import itob

_EXISTING_HINT: Final[str] = "the hint the account already has"


class FakeClient(ChangeCloudPassword):
    """A client that records the `hint` sent to `account.UpdatePasswordSettings`."""

    def __init__(self, *, hint: str | None) -> None:
        # A 127-bit Mersenne prime stands in for Telegram's own 2048-bit one: the SRP
        #  arithmetic below is the same either way and the small modulus keeps it instant.
        algo = raw.types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(
            salt1=b"salt1",
            salt2=b"salt2",
            g=3,
            p=itob((1 << 127) - 1),
        )

        self.password = raw.types.account.Password(
            new_algo=algo,
            new_secure_algo=raw.types.SecurePasswordKdfAlgoUnknown(),
            secure_random=b"secure-random",
            has_password=True,
            current_algo=algo,
            srp_B=itob(12345),
            srp_id=678,
            hint=hint,
        )
        self.captured_hint: str | None = "not-called"

    async def invoke(
        self,
        query: raw.functions.account.GetPassword | raw.functions.account.UpdatePasswordSettings,
    ) -> raw.types.account.Password | bool:
        if isinstance(query, raw.functions.account.GetPassword):
            return self.password

        self.captured_hint = query.new_settings.hint
        return True


@pytest.mark.asyncio
async def test_omitting_the_hint_keeps_the_existing_one() -> None:
    # `new_hint: str = ""` was sent straight through, so every password change that said
    #  nothing about the hint erased whatever hint the account had.
    client = FakeClient(hint=_EXISTING_HINT)

    await client.change_cloud_password("current_password", "new_password")

    assert client.captured_hint == _EXISTING_HINT


@pytest.mark.asyncio
async def test_an_explicit_hint_is_forwarded() -> None:
    client = FakeClient(hint=_EXISTING_HINT)

    await client.change_cloud_password("current_password", "new_password", new_hint="a new hint")

    assert client.captured_hint == "a new hint"


@pytest.mark.asyncio
async def test_an_empty_hint_clears_the_existing_one() -> None:
    client = FakeClient(hint=_EXISTING_HINT)

    await client.change_cloud_password("current_password", "new_password", new_hint="")

    assert client.captured_hint == ""


@pytest.mark.asyncio
async def test_an_account_with_no_hint_still_sends_a_string() -> None:
    # A hint is always on the wire, for the reason `change_cloud_password()` states, so an
    #  account that has none has to send an empty string and never `None`.
    client = FakeClient(hint=None)

    await client.change_cloud_password("current_password", "new_password")

    assert client.captured_hint == ""

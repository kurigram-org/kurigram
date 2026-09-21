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

import importlib
import importlib.util
from typing import Final

import pytest

from pyrogram.crypto import aes

_KEY: Final[bytes] = bytes(range(32))
_IGE_IV: Final[bytes] = bytes(range(32, 64))
_CTR_IV: Final[bytes] = bytes(range(64, 80))
_DATA: Final[bytes] = bytes(range(256)) * 4


def _backends() -> list[str]:
    return [name for name in ("warpcrypto", "tgcrypto") if importlib.util.find_spec(name)]


def test_ige_round_trips() -> None:
    encrypted = aes.ige256_encrypt(_DATA, _KEY, _IGE_IV)

    assert encrypted != _DATA
    assert aes.ige256_decrypt(encrypted, _KEY, _IGE_IV) == _DATA


def test_ctr_round_trips() -> None:
    encrypted = aes.ctr256_encrypt(_DATA, _KEY, bytearray(_CTR_IV), bytearray(1))

    assert encrypted != _DATA
    assert aes.ctr256_decrypt(encrypted, _KEY, bytearray(_CTR_IV), bytearray(1)) == _DATA


def test_ctr_advances_iv_and_state_in_place() -> None:
    iv, state = bytearray(_CTR_IV), bytearray(1)

    aes.ctr256_encrypt(_DATA, _KEY, iv, state)

    assert iv != _CTR_IV
    assert state == bytearray(1)


def test_ctr_resumes_from_the_state_it_was_left_in() -> None:
    iv, state = bytearray(_CTR_IV), bytearray(1)

    head = aes.ctr256_encrypt(_DATA[:24], _KEY, iv, state)
    tail = aes.ctr256_encrypt(_DATA[24:], _KEY, iv, state)

    assert head + tail == aes.ctr256_encrypt(_DATA, _KEY, bytearray(_CTR_IV), bytearray(1))


def test_xor_is_its_own_inverse() -> None:
    assert aes.xor(aes.xor(_DATA, _KEY * 32), _KEY * 32) == _DATA


@pytest.mark.skipif(len(_backends()) < 2, reason="needs both WarpCrypto and TgCrypto installed")
def test_backends_agree() -> None:
    warpcrypto = importlib.import_module("warpcrypto")
    tgcrypto = importlib.import_module("tgcrypto")

    assert warpcrypto.ige256_encrypt(_DATA, _KEY, _IGE_IV) == tgcrypto.ige256_encrypt(
        _DATA, _KEY, _IGE_IV
    )
    assert warpcrypto.ctr256_encrypt(
        _DATA, _KEY, bytearray(_CTR_IV), bytearray(1)
    ) == tgcrypto.ctr256_encrypt(_DATA, _KEY, bytearray(_CTR_IV), bytearray(1))

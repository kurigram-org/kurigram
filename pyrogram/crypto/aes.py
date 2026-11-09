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

import logging
from importlib import import_module

log = logging.getLogger(__name__)

_crypto_backend = None

for module_name in ["kuricrypt", "tgcrypto"]:
    try:
        _crypto_backend = import_module(module_name)
    except ImportError:
        continue

    log.info("Using %s as cryptography backend", module_name)
    break

if _crypto_backend is not None:

    def ige256_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
        return _crypto_backend.ige256_encrypt(data, key, iv)

    def ige256_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
        return _crypto_backend.ige256_decrypt(data, key, iv)

    def ctr256_encrypt(
        data: bytes, key: bytes, iv: bytearray, state: bytearray | None = None
    ) -> bytes:
        return _crypto_backend.ctr256_encrypt(data, key, iv, state or bytearray(1))

    def ctr256_decrypt(
        data: bytes, key: bytes, iv: bytearray, state: bytearray | None = None
    ) -> bytes:
        return _crypto_backend.ctr256_decrypt(data, key, iv, state or bytearray(1))
else:
    import pyaes

    from pyrogram import utils

    log.warning(
        "No optimized crypto library is available. "
        "Kurigram will work the same, but at a much slower speed. "
        "More info: https://docs.kurigram.icu/topics/speedups"
    )

    def ige256_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
        return ige(data, key, iv, True)

    def ige256_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
        return ige(data, key, iv, False)

    def ctr256_encrypt(
        data: bytes, key: bytes, iv: bytearray, state: bytearray | None = None
    ) -> bytes:
        return ctr(data, key, iv, state or bytearray(1))

    def ctr256_decrypt(
        data: bytes, key: bytes, iv: bytearray, state: bytearray | None = None
    ) -> bytes:
        return ctr(data, key, iv, state or bytearray(1))

    def ige(data: bytes, key: bytes, iv: bytes, encrypt: bool) -> bytes:
        cipher = pyaes.AES(key)

        iv_1 = iv[:16]
        iv_2 = iv[16:]

        data = [data[i : i + 16] for i in range(0, len(data), 16)]

        if encrypt:
            for i, chunk in enumerate(data):
                iv_1 = data[i] = utils.xor(cipher.encrypt(utils.xor(chunk, iv_1)), iv_2)
                iv_2 = chunk
        else:
            for i, chunk in enumerate(data):
                iv_2 = data[i] = utils.xor(cipher.decrypt(utils.xor(chunk, iv_2)), iv_1)
                iv_1 = chunk

        return b"".join(data)

    def ctr(data: bytes, key: bytes, iv: bytearray, state: bytearray) -> bytes:
        cipher = pyaes.AES(key)

        out = bytearray(data)
        chunk = cipher.encrypt(iv)

        for i in range(0, len(data), 16):
            for j in range(min(len(data) - i, 16)):
                out[i + j] ^= chunk[state[0]]

                state[0] += 1

                if state[0] >= 16:
                    state[0] = 0

                if state[0] == 0:
                    for k in range(15, -1, -1):
                        try:
                            iv[k] += 1
                            break
                        except ValueError:
                            iv[k] = 0

                    chunk = cipher.encrypt(iv)

        return bytes(out)

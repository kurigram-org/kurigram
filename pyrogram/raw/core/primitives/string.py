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

from typing import TYPE_CHECKING, Any

from ..tl_object import TLObject
from .bytes import Bytes

if TYPE_CHECKING:
    from io import BytesIO


# Not a `Bytes` subclass: `read` returns `str` where `Bytes.read` returns `bytes`,
#  so inheriting would break substitutability. The wire format is delegated instead.
class String(bytes, TLObject):
    @classmethod
    def read(cls, data: BytesIO, *args: Any) -> str:
        return Bytes.read(data).decode(errors="replace")

    def __new__(cls, value: str) -> bytes:
        return Bytes(value.encode())

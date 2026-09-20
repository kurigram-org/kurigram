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

from typing import TypeVar

ParsedType = TypeVar("ParsedType")


def require_parsed(value: ParsedType | None) -> ParsedType:
    """Unwrap a ``_parse`` result that the calling context guarantees to be present.

    The ``_parse`` helpers return ``None`` for empty raw objects (``UserEmpty``,
    ``ChatEmpty``, ...). Where Telegram must return the full object, a ``None``
    means a broken response and is raised instead of leaked to the caller.
    """
    if value is None:
        raise ValueError("Telegram returned an empty object where a full one was expected")

    return value

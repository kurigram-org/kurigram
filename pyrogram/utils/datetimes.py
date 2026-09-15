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

from datetime import datetime, timedelta, timezone


def zero_datetime() -> datetime:
    return datetime.fromtimestamp(0, timezone.utc)


def max_datetime() -> datetime:
    return datetime.fromtimestamp((1 << 31) - 1, timezone.utc)


def timestamp_to_datetime(ts: int | None) -> datetime | None:
    return datetime.fromtimestamp(ts) if ts else None


def datetime_to_timestamp(dt: datetime | timedelta | None) -> int | None:
    if isinstance(dt, timedelta):
        return int((datetime.now() + dt).timestamp())
    elif isinstance(dt, datetime):
        return int(dt.timestamp())

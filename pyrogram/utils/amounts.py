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


def from_nano(nano: int) -> float:
    return nano / 1e9


def to_nano(amount: float) -> int:
    return int(amount * 1e9)


def get_premium_duration_month_count(day_count: int) -> int:
    return max(1, day_count // 30)


def get_premium_duration_day_count(month_count: int) -> int:
    if month_count <= 0 or month_count > 10000000:
        return 7

    return month_count * 30 + month_count // 3 + month_count // 12

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

from pyrogram.utils.datetimes import datetime_to_timestamp

_MOMENT: Final[dt.datetime] = dt.datetime(2030, 1, 2, 3, 4, 5, tzinfo=dt.timezone.utc)


def test_datetime_becomes_its_timestamp() -> None:
    assert datetime_to_timestamp(_MOMENT) == int(_MOMENT.timestamp())


def test_none_stays_none() -> None:
    assert datetime_to_timestamp(None) is None


@pytest.mark.parametrize(
    "delta",
    [
        pytest.param(dt.timedelta(hours=1), id="future"),
        pytest.param(dt.timedelta(days=-1), id="past"),
    ],
)
def test_timedelta_is_counted_from_now(delta: dt.timedelta) -> None:
    earliest = int((dt.datetime.now() + delta).timestamp())
    timestamp = datetime_to_timestamp(delta)
    latest = int((dt.datetime.now() + delta).timestamp())

    assert timestamp is not None
    assert earliest <= timestamp <= latest

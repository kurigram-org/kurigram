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

import asyncio

from collections import OrderedDict

from typing import Any


class Cache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be greater than 0")

        self.capacity = capacity
        self._cache: OrderedDict[Any, Any] = OrderedDict()
        self._lock = asyncio.Lock()

    # Rebuilds the lock and keeps what is cached. Why it has to be rebuilt at all is on
    #  `Client._rebuild_loop_bound_state`.
    def reset_lock(self) -> None:
        self._lock = asyncio.Lock()

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: Any) -> bool:
        return key in self._cache

    def __bool__(self) -> bool:
        return bool(self._cache)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(capacity={self.capacity}, size={len(self)})"

    async def get(self, key: Any, default: Any = None) -> Any:
        async with self._lock:
            if key not in self._cache:
                return default

            self._cache.move_to_end(key)
            return self._cache[key]

    async def set(self, key: Any, value: Any) -> None:
        async with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)

            if len(self._cache) > self.capacity:
                self._cache.popitem(last=False)

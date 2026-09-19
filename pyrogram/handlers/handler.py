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
import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    import pyrogram
    from pyrogram.filters import Filter
    from pyrogram.types import Update

if TYPE_CHECKING:
    from pyrogram.raw.base import Update as RawUpdate

# Every subclass binds this to the callback it dispatches, so `handler.callback` keeps
#  the signature that subclass documents. A bare `Callable` erased it, and a call with
#  the wrong number of arguments passed unremarked.
#
#  Each of them spells its callback as a module-level alias, so the base-class subscript
#  and the `__init__` signature cannot drift apart. A base-class subscript is evaluated at
#  import time, which `from __future__ import annotations` does not defer, so an alias
#  quotes `pyrogram.Client`: `pyrogram/__init__.py` binds `Client` only after it has
#  imported this package.
CallbackType = TypeVar("CallbackType", bound=Callable[..., Any])


class Handler(Generic[CallbackType]):
    def __init__(self, callback: CallbackType, filters: Filter | None = None) -> None:
        self.callback = callback
        self.filters = filters

    async def check(self, client: pyrogram.Client, update: Update | RawUpdate) -> bool:
        if callable(self.filters):
            if inspect.iscoroutinefunction(self.filters.__call__):
                return await self.filters(client, update)
            else:
                return await asyncio.get_running_loop().run_in_executor(
                    client.executor, self.filters, client, update
                )

        return True

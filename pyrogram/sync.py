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
import functools
import inspect
from collections.abc import AsyncIterator, Generator
from typing import Any

from pyrogram import types, utils
from pyrogram.methods import Methods
from pyrogram.methods.utilities import idle as idle_module, compose as compose_module


def async_to_sync(obj, name):
    function = getattr(obj, name)

    def async_to_sync_gen(
        agen: AsyncIterator[Any],
        *,
        loop: asyncio.AbstractEventLoop,
    ) -> Generator[Any, None, None]:
        async def anext(agen):
            try:
                return await agen.__anext__(), False
            except StopAsyncIteration:
                return None, True

        while True:
            if loop.is_running():
                item, done = asyncio.run_coroutine_threadsafe(anext(agen), loop).result()
            else:
                item, done = loop.run_until_complete(anext(agen))

            if done:
                break

            yield item

    @functools.wraps(function)
    def async_to_sync_wrap(*args, **kwargs):
        coroutine = function(*args, **kwargs)

        # Both loops are resolved here rather than in `async_to_sync`: `wrap()` below runs
        #  during `import pyrogram`, when there is no loop to resolve them against yet.
        target_loop = utils.get_event_loop()
        caller_loop = utils.get_running_loop()

        # The caller is already on the loop the coroutine belongs to, so it awaits it itself.
        if caller_loop is target_loop:
            return coroutine

        if inspect.isasyncgen(coroutine):
            if caller_loop is not None:
                return coroutine

            return async_to_sync_gen(coroutine, loop=target_loop)

        if caller_loop is not None:
            return asyncio.wrap_future(asyncio.run_coroutine_threadsafe(coroutine, target_loop))

        # No loop in this thread: either the application is running one elsewhere (a handler
        #  in `Client.executor` lands here), or nobody has started one and we drive it.
        if target_loop.is_running():
            return asyncio.run_coroutine_threadsafe(coroutine, target_loop).result()

        return target_loop.run_until_complete(coroutine)

    setattr(obj, name, async_to_sync_wrap)


def wrap(source):
    for name in dir(source):
        method = getattr(source, name)

        if not name.startswith("_"):
            if inspect.iscoroutinefunction(method) or inspect.isasyncgenfunction(method):
                async_to_sync(source, name)


# Wrap all Client's relevant methods
wrap(Methods)

# Wrap types' bound methods
for class_name in dir(types):
    cls = getattr(types, class_name)

    if inspect.isclass(cls):
        wrap(cls)

# Special case for idle and compose, because they are not inside Methods
async_to_sync(idle_module, "idle")
idle = idle_module.idle

async_to_sync(compose_module, "compose")
compose = compose_module.compose

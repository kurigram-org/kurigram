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


# The loop the library runs on, recorded by `get_event_loop()` below the first time it is
#  asked from inside one, which is `Client.loop` during `start()`. It cannot be resolved at
#  import: `pyrogram/sync.py` wraps every method before anything is running one.
_loop: asyncio.AbstractEventLoop | None = None


def get_running_loop() -> asyncio.AbstractEventLoop | None:
    """Return the loop the calling thread is inside, or `None`. Never builds one."""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return None


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Return the loop the library runs on, recording it when the caller is inside one."""
    # Rebinding it is the point: a thread with no loop of its own cannot reach the one
    #  the client runs on any other way.
    global _loop  # noqa: PLW0603

    recorded = _loop
    running = get_running_loop()

    # A recorded loop that is not running was either built below for a caller that had
    #  none, or closed by whoever ran it. A loop running now is the one the application
    #  drives, so it wins.
    if running is not None and (recorded is None or not recorded.is_running()):
        recorded = running

    if recorded is None or recorded.is_closed():
        recorded = asyncio.new_event_loop()
        asyncio.set_event_loop(recorded)

    _loop = recorded

    return recorded

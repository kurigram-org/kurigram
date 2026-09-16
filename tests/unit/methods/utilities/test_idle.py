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


"""`idle()` hands the signal handlers back to whoever installed them.

The handler it installs closes over the loop `idle()` ran on, and `run()` closes that loop
when it returns. A signal arriving afterwards used to run a handler that raised
`RuntimeError: Event loop is closed` out of the signal handler itself.
"""

from __future__ import annotations as _annotations

import asyncio
import signal
from signal import SIGABRT, SIGINT, SIGTERM
from typing import Final

from pyrogram import idle

_WATCHED: Final[tuple[signal.Signals, ...]] = (SIGINT, SIGTERM, SIGABRT)


async def test_idle_restores_every_handler_it_replaced() -> None:
    before = {number: signal.getsignal(number) for number in _WATCHED}

    idling = asyncio.create_task(idle())

    # Nothing announces that `idle()` has installed them, and it only does so once it has
    #  the running loop, which is after this task first yields.
    while signal.getsignal(SIGINT) is before[SIGINT]:
        await asyncio.sleep(0)

    installed = {number: signal.getsignal(number) for number in _WATCHED}

    # What a Ctrl+C does: the handler `idle()` installed cancels the task it is waiting on.
    signal.raise_signal(SIGINT)
    await asyncio.wait_for(idling, 1)

    assert all(installed[number] is not before[number] for number in _WATCHED)
    assert {number: signal.getsignal(number) for number in _WATCHED} == before

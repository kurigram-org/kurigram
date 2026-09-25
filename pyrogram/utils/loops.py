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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Coroutine

try:
    import uvloop  # ty: ignore[unresolved-import] - optional dependency, extra `fast`
# No warning on this branch, unlike the `TgCrypto` one in `pyrogram/crypto/aes.py`:
#  `uvloop` has no Windows wheel, so there its absence is the only possible state,
#  not a degradation worth reporting.
except ImportError:
    uvloop = None


def new_event_loop() -> asyncio.AbstractEventLoop:
    """Build a fresh event loop: `uvloop`'s when it is installed, `asyncio`'s otherwise."""
    if uvloop is None:
        return asyncio.new_event_loop()

    return uvloop.new_event_loop()


def run(main: Coroutine[Any, Any, None]) -> None:
    """`asyncio.run`, on `uvloop`'s loop when it is installed."""
    if uvloop is None:
        asyncio.run(main)
        return

    # Not `asyncio.run(main, loop_factory=...)`: `loop_factory` needs Python 3.12 and the
    #  package floor is 3.10. `uvloop.run` carries its own runner for the older versions.
    #  https://docs.python.org/3/library/asyncio-runner.html#asyncio.run
    uvloop.run(main)

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

import copy
import pickle
from typing import Final, Protocol

import pytest

from pyrogram import enums
from pyrogram.types.user_and_chats.user import Link

_URL: Final[str] = "https://example.com"
_TEXT: Final[str] = "label"
_STYLE: Final[enums.ParseMode] = enums.ParseMode.HTML
_LINK: Final[Link] = Link(_URL, _TEXT, _STYLE)

# Protocol 0 and 1 refuse any `__slots__` class that does not define `__getstate__` of its
#  own, `Str` included, so they are not `Link`'s to fix. The default protocol is 5.
#  https://github.com/python/cpython/blob/323c59a5e348347be2ce2b7ea55fcb30bf68b2d3/Lib/copyreg.py#L91-L94
_PICKLE_PROTOCOLS: Final[tuple[int, ...]] = tuple(range(2, pickle.HIGHEST_PROTOCOL + 1))


class Copier(Protocol):
    def __call__(self, link: Link, /) -> Link: ...


def state(link: Link) -> dict[str, str | enums.ParseMode]:
    """Everything a round trip has to bring back, the string half included."""
    # `str.__str__` reads the string the object was built from. `Link.__str__` recomputes it
    #  from the three attributes, so it would agree even with an empty string underneath.
    return {
        "class": type(link).__name__,
        "value": str.__str__(link),
        "url": link.url,
        "text": link.text,
        "style": link.style,
    }


@pytest.mark.parametrize(
    "copier",
    [
        pytest.param(copy.copy, id="copy"),
        pytest.param(copy.deepcopy, id="deepcopy"),
    ],
)
def test_copying_a_link_preserves_its_url_text_and_style(copier: Copier) -> None:
    assert state(copier(_LINK)) == state(_LINK)


@pytest.mark.parametrize(
    "protocol",
    [pytest.param(protocol, id=f"protocol-{protocol}") for protocol in _PICKLE_PROTOCOLS],
)
def test_pickling_a_link_preserves_its_url_text_and_style(protocol: int) -> None:
    round_tripped: Link = pickle.loads(pickle.dumps(_LINK, protocol))

    assert state(round_tripped) == state(_LINK)

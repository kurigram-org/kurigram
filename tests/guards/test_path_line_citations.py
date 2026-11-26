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

"""No comment cites a file by line number.

A `path:line` citation is right on the day it is written and wrong after the next edit above
that line, with nothing to notice: no check opens the cited file to see what that line holds
now. When this guard was written, one of five such citations had already drifted, `tcp.py:505` pointing at
the `_connect` signature instead of the `raise` in `send` the comment was about, and the next
schema update moved the four `main_api.tl` ones as well. A comment names the function or
the TL constructor instead, which is found by a search and does not move.

The line is matched in every spelling a comment uses for it: `tcp.py:505`, `tcp.py:L505`,
`tcp.py#L505`, and a backticked path followed by `:505`. A permalink is not a citation of
this kind: it is pinned to a commit, so its line cannot move. URLs are removed before the
search, which is what lets a permalink's `#L253` through and also keeps a `host:port`
inside one from reading as a citation.
"""

from __future__ import annotations as _annotations

import io
import re
import tokenize
from itertools import chain
from typing import TYPE_CHECKING, Final

from tests.guards.name_resolution import (
    REPOSITORY_ROOT,
    hand_written_files,
    source_of,
    tooling_files,
)

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator

_PATH_LINE: Final[re.Pattern[str]] = re.compile(r"\w\.[A-Za-z]\w*`?(?::L?|#L)\d+")
_URL: Final[re.Pattern[str]] = re.compile(r"\w+://\S+")


def path_line_citations(source: str) -> list[int]:
    """The line of every comment in `source` that cites a file by line number."""
    found: list[int] = []

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue

        if _PATH_LINE.search(_URL.sub("", token.string)):
            found.append(token.start[0])

    return found


def swept_modules() -> Iterator[pathlib.Path]:
    return chain(hand_written_files(), tooling_files())


def comments_citing_a_line() -> list[str]:
    found: list[str] = []

    for path in swept_modules():
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        found.extend(f"{relative}:{line}" for line in path_line_citations(source_of(path)))

    return found


def test_no_comment_cites_a_file_by_line_number() -> None:
    assert comments_citing_a_line() == []


def test_the_sweep_reads_the_modules_it_claims_to() -> None:
    swept = [path.relative_to(REPOSITORY_ROOT).as_posix() for path in swept_modules()]

    assert len(swept) > 700

    # One from each root, so a walk that drops a root or reads nothing fails here rather than
    #  passing quietly.
    assert "pyrogram/client.py" in swept
    assert "tests/guards/test_path_line_citations.py" in swept
    assert "compiler/api/compiler.py" in swept


def test_the_sweep_reads_both_halves_of_what_it_asks() -> None:
    assert path_line_citations("# `compiler/api/source/main_api.tl:2188`\n") == [1]
    assert path_line_citations("x = 1  # see `pyrogram/session/session.py:728`.\n") == [1]
    assert path_line_citations("# the markers are mapped in `conftest.py:37`\n") == [1]

    # The failure names the line of the comment, so a citation below the first line is pinned.
    assert path_line_citations("x = 1\n\n# see `conftest.py:37`\n") == [3]

    # The other spellings of the same line number, each of which moves just the same.
    assert path_line_citations("# see `tcp.py#L505`\n") == [1]
    assert path_line_citations("# see `tcp.py:L505`\n") == [1]
    assert path_line_citations("# see `pyrogram/session/session.py`:728\n") == [1]

    assert (
        path_line_citations("# `keyboardButtonStyle` in `compiler/api/source/main_api.tl`\n") == []
    )
    assert (
        path_line_citations(
            "# https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsInit.cpp#L253\n"
        )
        == []
    )
    assert path_line_citations("# https://proxy.example.com:1080/path\n") == []
    # Any scheme is a URL, and a proxy one is the likeliest to carry a port.
    assert path_line_citations("# socks5://proxy.example.com:1080\n") == []

    # A citation inside a string is data, which is why this reads tokens and not lines.
    assert path_line_citations('expected = "probe.py:13: Bound.event"\n') == []

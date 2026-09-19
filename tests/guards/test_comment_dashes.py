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

"""No comment uses a long dash, or a `--`, as punctuation.

`CONTRIBUTING.md` has asked for this under "Code style conventions" since the file was
written, and nothing read it: `ruff` has no rule for either, so every occurrence had to be
caught by a person in review, and they kept arriving. The one this guard was written for was
a `# noqa: F403 -- reason`, which is also the shape most likely to come back, because the
reason after a code reads like a place where any punctuation will do.

Every format the repository writes `#` comments in is read, not only Python. The guard used
to walk `*.py` alone, and `pyproject.toml` went out carrying
`# pyupgrade - outdated typing syntax` with a long dash in place of that `-`, with the whole
suite green. Python is read with `tokenize`, which only understands Python; the others are
read a line at a time, taking the first `#` that is outside a quoted value.

Docstrings are deliberately out of scope. Thirteen of them carry a dash, almost all copied
from Telegram's own API documentation, and rewriting somebody else's prose is a different
change from holding our own comments to a rule.
"""

from __future__ import annotations as _annotations

import io
import re
import tokenize
from itertools import chain
from typing import Final

from tests.guards.name_resolution import (
    REPOSITORY_ROOT,
    configuration_files,
    hand_written_files,
    source_of,
    tooling_files,
)

# En dash, em dash, figure dash and horizontal bar: the whole family, because the one that
#  gets pasted in depends on the editor rather than on what was meant.
_LONG_DASH: Final[re.Pattern[str]] = re.compile(r"[‒–—―]")

# A `--` is punctuation only between two words. `--fix` is a flag, and `grep -v -- -` is the
#  end-of-options marker, so both keep their dashes.
_DOUBLE_DASH: Final[re.Pattern[str]] = re.compile(r"(?<=\w)\s+--\s+(?=\w)")

# What opens a comment in TOML, YAML and a `Makefile`: a `#` at the start of the line or
#  after whitespace. A quoted value is blanked out first, so a `#` inside one opens nothing.
_QUOTED: Final[re.Pattern[str]] = re.compile(r"\"[^\"]*\"|'[^']*'")
_COMMENT_OPENER: Final[re.Pattern[str]] = re.compile(r"(?:^|\s)#")


def dashes_in_comments(source: str) -> list[int]:
    """The line of every comment in `source` that uses a long dash or a `--` as punctuation."""
    found: list[int] = []

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue

        if _LONG_DASH.search(token.string) or _DOUBLE_DASH.search(token.string):
            found.append(token.start[0])

    return found


def hash_comment(line: str) -> str | None:
    """What a `#` opens on `line`, or `None` when the line opens no comment at all."""
    masked = _QUOTED.sub(lambda quoted: "_" * len(quoted.group()), line)
    opener = _COMMENT_OPENER.search(masked)

    if opener is None:
        return None

    return line[opener.end() - 1 :]


def dashes_in_hash_comments(source: str) -> list[int]:
    """The line of every `#` comment in a non-Python `source` that uses a dash as punctuation."""
    found: list[int] = []

    for number, line in enumerate(source.splitlines(), start=1):
        comment = hash_comment(line)

        if comment is None:
            continue

        if _LONG_DASH.search(comment) or _DOUBLE_DASH.search(comment):
            found.append(number)

    return found


def comments_using_a_dash() -> list[str]:
    found: list[str] = []

    for path in chain(hand_written_files(), tooling_files()):
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        found.extend(f"{relative}:{line}" for line in dashes_in_comments(source_of(path)))

    for path in configuration_files():
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        found.extend(f"{relative}:{line}" for line in dashes_in_hash_comments(source_of(path)))

    return found


def test_no_comment_uses_a_dash_as_punctuation() -> None:
    assert comments_using_a_dash() == []


def test_the_sweep_reads_the_modules_it_claims_to() -> None:
    swept = [
        path.relative_to(REPOSITORY_ROOT).as_posix()
        for path in chain(hand_written_files(), tooling_files())
    ]

    assert len(swept) > 700

    # One from each root, so dropping a root fails here rather than passing quietly.
    assert "pyrogram/client.py" in swept
    assert "tests/guards/test_comment_dashes.py" in swept
    assert "compiler/api/compiler.py" in swept


def test_the_sweep_reads_both_halves_of_what_it_asks() -> None:
    assert dashes_in_comments("# noqa: F403 -- generated by `make api`\n") == [1]
    assert dashes_in_comments("value = 1  # kept for the gateway — it 502s otherwise\n") == [1]

    assert dashes_in_comments("# noqa: F403 - generated by `make api`\n") == []
    assert dashes_in_comments("# grep -v -- - public.key | tr -d\n") == []
    assert dashes_in_comments("# uv run ruff check --fix\n") == []

    # A comment inside a string is a string, which is why this reads tokens and not lines.
    assert dashes_in_comments('text = "# a -- b — c"\n') == []


def test_the_sweep_reads_every_format_it_claims_to() -> None:
    swept = [path.relative_to(REPOSITORY_ROOT).as_posix() for path in configuration_files()]

    # One per format, so dropping a format fails here rather than passing quietly.
    assert "pyproject.toml" in swept
    assert ".github/workflows/python.yml" in swept
    assert ".pre-commit-config.yaml" in swept
    assert "Makefile" in swept
    assert ".gitignore" in swept


def test_the_line_reader_reads_both_halves_of_what_it_asks() -> None:
    assert dashes_in_hash_comments('select = [\n  "UP",  # pyupgrade — outdated syntax\n]\n') == [2]
    assert dashes_in_hash_comments("# the floor -- and the ceiling -- are both tested\n") == [1]

    assert dashes_in_hash_comments("        args: [--fix, --exit-non-zero-on-fix]  # ruff\n") == []
    assert dashes_in_hash_comments("\tgrep -v -- - public.key  # drop the marker\n") == []
    assert dashes_in_hash_comments("# pyupgrade - outdated typing syntax\n") == []

    # A `#` inside a quoted value opens no comment, so a dash after one is data.
    assert dashes_in_hash_comments('name = "a # b — c"\n') == []

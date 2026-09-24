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

"""Every `Message.reply_*` and `Message.answer_*` shortcut accepts what its target accepts.

A shortcut that omits a parameter of the `Client.send_*` it wraps cannot reach that feature at
all, and nothing else reports the gap: both signatures are valid on their own, and the omission
only shows up as a caller wondering why the option has no effect.
"""

from __future__ import annotations as _annotations

import ast
import inspect
import re
import sys
import textwrap
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import pytest

from pyrogram import Client, types

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import ModuleType


@dataclass(frozen=True)
class Shortcut:
    """A bound method on `Message` and the client method its docstring says it wraps."""

    name: str
    target_name: str


_TARGET: Final[re.Pattern[str]] = re.compile(r"Shortcut for method :obj:`~pyrogram\.Client\.(\w+)`")

# The shortcut's own docstring lists what it fills from `self`, one bullet per attribute.
_FILLED_FROM_SELF: Final[re.Pattern[str]] = re.compile(r"^\* (\w+)$", re.MULTILINE)

# Each `send_*` module warns about its own retired parameters with this exact wording, so which
#  ones are retired is read off the target rather than listed here. A name can be deprecated in
#  one target and current in another: `parse_mode` only feeds `quote_parse_mode` in
#  `send_contact`, while in `send_photo` it parses the caption.
_DEPRECATED: Final[re.Pattern[str]] = re.compile(r"`(\w+)` is deprecated")


def shortcut_names() -> list[str]:
    return sorted(name for name in vars(types.Message) if name.startswith(("reply_", "answer_")))


def shortcuts() -> Iterator[Shortcut]:
    for name in shortcut_names():
        match = _TARGET.search(inspect.getdoc(vars(types.Message)[name]) or "")

        if match is not None:
            yield Shortcut(
                name=name,
                target_name=match.group(1),
            )


_SHORTCUTS: Final[list[Shortcut]] = list(shortcuts())


def filled_from_self(shortcut: Shortcut) -> set[str]:
    return set(
        _FILLED_FROM_SELF.findall(inspect.getdoc(getattr(types.Message, shortcut.name)) or "")
    )


def deprecated_in(module: ModuleType) -> set[str]:
    return set(_DEPRECATED.findall(inspect.getsource(module)))


# Read the call rather than the source text: `ruff format` joins a call that fits on one line,
#  and a regex looking for `name=name` on a line of its own then reports the name as dropped.
def keywords_of(shortcut: Shortcut) -> Iterator[ast.keyword]:
    """Every keyword argument of every call the shortcut makes."""
    source = textwrap.dedent(inspect.getsource(getattr(types.Message, shortcut.name)))

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            yield from node.keywords


def forwarded_by(shortcut: Shortcut) -> set[str]:
    """Every name the shortcut hands straight on, written `name=name` in a call it makes."""
    return {
        keyword.arg
        for keyword in keywords_of(shortcut)
        if isinstance(keyword.value, ast.Name) and keyword.arg == keyword.value.id
    }


def passed_by(shortcut: Shortcut) -> set[str]:
    """Every keyword the shortcut passes on, whatever the value is built from."""
    return {keyword.arg for keyword in keywords_of(shortcut) if keyword.arg is not None}


def parameters_the_caller_must_supply(shortcut: Shortcut) -> list[str]:
    target = getattr(Client, shortcut.target_name)
    ignored: set[str] = (
        filled_from_self(shortcut) | deprecated_in(sys.modules[target.__module__]) | {"self"}
    )

    return [name for name in inspect.signature(target).parameters if name not in ignored]


def test_every_shortcut_is_discovered() -> None:
    # The scan reads the docstring, so a reworded first line would quietly drop a method from
    #  every check below and leave the suite green.
    discovered = {shortcut.name for shortcut in _SHORTCUTS}

    assert sorted(discovered) == shortcut_names()


@pytest.mark.parametrize("shortcut", _SHORTCUTS, ids=[shortcut.name for shortcut in _SHORTCUTS])
def test_a_shortcut_names_a_client_method_that_exists(shortcut: Shortcut) -> None:
    assert hasattr(Client, shortcut.target_name)


@pytest.mark.parametrize("shortcut", _SHORTCUTS, ids=[shortcut.name for shortcut in _SHORTCUTS])
def test_a_shortcut_accepts_everything_its_target_accepts(shortcut: Shortcut) -> None:
    accepted = set(inspect.signature(getattr(types.Message, shortcut.name)).parameters)
    missing = [name for name in parameters_the_caller_must_supply(shortcut) if name not in accepted]

    assert not missing


@pytest.mark.parametrize("shortcut", _SHORTCUTS, ids=[shortcut.name for shortcut in _SHORTCUTS])
def test_a_shortcut_forwards_everything_it_accepts(shortcut: Shortcut) -> None:
    # A parameter in the signature that the call never passes on is worse than a missing one:
    #  the caller gets no error and the option is dropped.
    accepted = inspect.signature(getattr(types.Message, shortcut.name)).parameters
    wanted = set(parameters_the_caller_must_supply(shortcut))
    forwarded = forwarded_by(shortcut)

    dropped = [name for name in accepted if name in wanted and name not in forwarded]

    assert not dropped


@pytest.mark.parametrize("shortcut", _SHORTCUTS, ids=[shortcut.name for shortcut in _SHORTCUTS])
def test_a_shortcut_fills_everything_its_docstring_claims_it_fills(shortcut: Shortcut) -> None:
    # A bullet is what excuses a name from both checks above, so a bullet the call never passes
    #  hides the gap rather than reporting it. `reply_rich` and `answer_rich` both listed
    #  `business_connection_id` while neither passed it, and the suite stayed green.
    accepted = set(inspect.signature(getattr(Client, shortcut.target_name)).parameters)
    passed = passed_by(shortcut)

    unfilled = sorted(
        name for name in filled_from_self(shortcut) if name in accepted and name not in passed
    )

    assert not unfilled

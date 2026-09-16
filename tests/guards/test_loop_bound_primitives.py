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


"""Nothing that binds to an event loop is built once and kept.

An `asyncio.Queue`, `Event`, `Lock` or `Semaphore` binds to the first loop that awaits it
and raises `RuntimeError: <repr> is bound to a different event loop` for every other one.
Building one in `__init__` therefore ties the object to whichever loop it first meets, and
a second `Client.run()` died on exactly that. Each must be rebuilt when a loop exists.
https://github.com/python/cpython/blob/323c59a5e348347be2ce2b7ea55fcb30bf68b2d3/Lib/asyncio/mixins.py#L19
"""

from __future__ import annotations as _annotations

import ast
from dataclasses import dataclass
from typing import Final
from collections.abc import Iterator

from tests.guards.name_resolution import REPOSITORY_ROOT

_SWEPT: Final[tuple[str, ...]] = ("pyrogram/client.py", "pyrogram/dispatcher.py")

_LOOP_BOUND: Final[frozenset[str]] = frozenset({"Queue", "Event", "Lock", "Semaphore"})


@dataclass(frozen=True, slots=True)
class Attribute:
    """One `self.<name>` built in an `__init__`, and where it was found."""

    file: str
    owner: str
    name: str
    line: int

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.owner}.{self.name}"


def assigned_attributes(node: ast.AST) -> Iterator[tuple[str, ast.expr, int]]:
    for statement in ast.walk(node):
        if isinstance(statement, ast.AnnAssign):
            targets, value = [statement.target], statement.value
        elif isinstance(statement, ast.Assign):
            targets, value = statement.targets, statement.value
        else:
            continue

        if value is None:
            continue

        for target in targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                yield target.attr, value, target.lineno


def builds_a_loop_bound_primitive(value: ast.expr) -> bool:
    if not isinstance(value, ast.Call):
        return False

    called = value.func

    return (
        isinstance(called, ast.Attribute)
        and isinstance(called.value, ast.Name)
        and called.value.id == "asyncio"
        and called.attr in _LOOP_BOUND
    )


def methods(node: ast.ClassDef) -> Iterator[ast.FunctionDef | ast.AsyncFunctionDef]:
    for statement in node.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield statement


def primitives_never_rebuilt(tree: ast.Module, *, file: str) -> list[Attribute]:
    found: list[Attribute] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        built_by_the_constructor: list[Attribute] = []
        rebuilt: set[str] = set()

        for method in methods(node):
            for name, value, line in assigned_attributes(method):
                if method.name == "__init__":
                    if builds_a_loop_bound_primitive(value):
                        built_by_the_constructor.append(
                            Attribute(
                                file=file,
                                owner=node.name,
                                name=name,
                                line=line,
                            )
                        )

                else:
                    rebuilt.add(name)

        found.extend(
            attribute for attribute in built_by_the_constructor if attribute.name not in rebuilt
        )

    return found


def swept() -> Iterator[tuple[str, ast.Module]]:
    for file in _SWEPT:
        yield file, ast.parse((REPOSITORY_ROOT / file).read_text(), filename=file)


def test_every_loop_bound_primitive_is_rebuilt_somewhere() -> None:
    offenders = [
        str(attribute)
        for file, tree in swept()
        for attribute in primitives_never_rebuilt(tree, file=file)
    ]

    assert offenders == []


def test_the_sweep_finds_the_primitives_it_is_about() -> None:
    built_by_the_constructor = {
        f"{node.name}.{name}"
        for _, tree in swept()
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
        for method in methods(node)
        if method.name == "__init__"
        for name, value, _ in assigned_attributes(method)
        if builds_a_loop_bound_primitive(value)
    }

    assert built_by_the_constructor == {
        "Cache._lock",
        "Client.get_file_semaphore",
        "Client.save_file_semaphore",
        "Client.sessions_lock",
        "Client.updates_watchdog_event",
        "Dispatcher.updates_queue",
    }


def test_the_sweep_reports_a_primitive_nothing_rebuilds() -> None:
    source: str = (
        "import asyncio\n"
        "\n"
        "class Kept:\n"
        "    def __init__(self):\n"
        "        self.queue = asyncio.Queue()\n"
        "        self.plain = []\n"
        "\n"
        "    def reset(self):\n"
        "        self.queue = asyncio.Queue()\n"
        "\n"
        "class Bound:\n"
        "    def __init__(self):\n"
        "        self.event: asyncio.Event = asyncio.Event()\n"
    )

    found = primitives_never_rebuilt(ast.parse(source), file="probe.py")

    assert [str(attribute) for attribute in found] == ["probe.py:13: Bound.event"]

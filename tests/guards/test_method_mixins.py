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

"""Every method mixin under `pyrogram/methods/` is a base of `pyrogram.Client`.

A mixin there holds one method and nothing else, and it reaches a caller only once a package
`__init__.py` both imports it and names it among the bases of that package's aggregate class.
Both halves are hand-written lists of eighty-odd entries, nothing checks either, and an
omission is invisible until somebody calls the method and gets `AttributeError`.

It has gone wrong twice. `EditFolderInviteLink` was written with a full docstring and never
imported, so `Client.edit_folder_invite_link` did not exist while its three siblings did;
`SetBotProfilePhoto` was the same defect, fixed the same way.

The sweep asks `issubclass` rather than "does some `__init__.py` name this class", because a
class imported into the barrel and left off the bases list is the other half of the same
defect and reads as wired up.
"""

from __future__ import annotations as _annotations

import ast
import importlib
from typing import Final, TYPE_CHECKING

import pyrogram

from tests.guards.name_resolution import PACKAGE_ROOT, REPOSITORY_ROOT

if TYPE_CHECKING:
    import pathlib

_MIXIN_ROOT: Final[pathlib.Path] = PACKAGE_ROOT / "methods"

# A mixin left unreachable on purpose goes here by dotted name so the suite stays green;
#  `test_every_exemption_is_still_earned` fails the day it is wired up, so an entry cannot
#  outlive the debt it records.
_UNREACHABLE_MIXINS: Final[tuple[str, ...]] = ()


def defines_a_public_method(node: ast.ClassDef) -> bool:
    """Whether the class contributes a method to `Client`, which is what makes it a mixin.

    The discriminator, rather than a list of what to skip: a class under `pyrogram/methods/`
    exists to put a method on `Client`, so one that contributes none is a helper. That drops
    the two `decorators` dataclasses, whose bodies are field declarations, and every aggregate
    class, whose body is `pass`.
    """
    return any(
        isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not statement.name.startswith("_")
        for statement in node.body
    )


def module_name(path: pathlib.Path) -> str:
    parts = path.relative_to(REPOSITORY_ROOT).with_suffix("").parts

    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def mixin_names(tree: ast.Module) -> list[str]:
    """Every class the module defines that contributes a method."""
    return [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and defines_a_public_method(node)
    ]


def declared_mixins() -> list[str]:
    """The dotted name of every method mixin the tree defines, wired up or not."""
    found: list[str] = []

    for path in sorted(_MIXIN_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=path.name)
        module = module_name(path)

        found.extend(f"{module}.{name}" for name in mixin_names(tree))

    return found


def reaches_the_client(dotted: str) -> bool:
    """Import the mixin by its dotted name and ask whether `Client` inherits from it.

    The import is what the sweep needs and `pyrogram` cannot give: a mixin nobody wired up is
    by construction absent from every package the client pulls in.
    """
    module, _, name = dotted.rpartition(".")

    return issubclass(pyrogram.Client, getattr(importlib.import_module(module), name))


def unreachable_mixins() -> list[str]:
    return [dotted for dotted in declared_mixins() if not reaches_the_client(dotted)]


def parsed_class(source: str) -> ast.ClassDef:
    node = ast.parse(source).body[0]

    assert isinstance(node, ast.ClassDef)

    return node


def test_every_mixin_reaches_the_client() -> None:
    assert [dotted for dotted in unreachable_mixins() if dotted not in _UNREACHABLE_MIXINS] == []


def test_every_exemption_is_still_earned() -> None:
    # An entry left behind after its method was wired up is where the next orphan hides.
    unreachable = unreachable_mixins()

    assert [dotted for dotted in _UNREACHABLE_MIXINS if dotted not in unreachable] == []


def test_the_sweep_reads_the_mixins_it_claims_to() -> None:
    declared = declared_mixins()

    assert len(declared) > 380

    for expected in (
        "pyrogram.methods.chats.edit_folder_invite_link.EditFolderInviteLink",
        "pyrogram.methods.decorators.on_message.OnMessage",
        "pyrogram.methods.utilities.stop_transmission.StopTransmission",
    ):
        assert expected in declared


def test_the_sweep_takes_a_helper_for_what_it_is() -> None:
    declared = declared_mixins()

    # Both are return types of the decorator helpers, read inside their own module.
    assert "pyrogram.methods.decorators.unbound_arguments.UnboundArguments" not in declared
    assert "pyrogram.methods.decorators.unbound_arguments.UnboundErrorArguments" not in declared

    # An aggregate class inherits its methods and declares none, so it is not a mixin either.
    assert "pyrogram.methods.chats.Chats" not in declared


def test_the_discriminator_reads_both_halves_of_what_it_asks() -> None:
    assert defines_a_public_method(parsed_class("class Thing:\n    def do(self):\n        pass\n"))

    assert not defines_a_public_method(parsed_class("class Thing:\n    field: int\n"))
    assert not defines_a_public_method(parsed_class("class Thing:\n    pass\n"))

    # A private method is somebody's implementation detail, never what a caller reaches for.
    assert not defines_a_public_method(
        parsed_class("class Thing:\n    def _do(self):\n        pass\n")
    )


def test_the_sweep_resolves_a_name_the_client_does_not_carry() -> None:
    # The sweep would report nothing at all if `reaches_the_client` answered `True` for
    #  everything, which is the way a guard like this fails silently.
    assert reaches_the_client(
        "pyrogram.methods.chats.create_folder_invite_link.CreateFolderInviteLink"
    )
    assert not reaches_the_client("pyrogram.methods.decorators.unbound_arguments.UnboundArguments")

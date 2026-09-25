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

"""Write the "porting from Pyrogram" page by diffing this tree against the last Pyrogram release.

Run from the repository root: `python compiler/docs/porting.py`. `make docs` does it.
"""

from __future__ import annotations as _annotations

import ast
import io
import subprocess
import sys
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

# The reference is the last Pyrogram release, resolved from this repository's own tags:
#  that project's releases all live in `v2.0.*` (the last is `v2.0.106`, 2023-04-30) and
#  Kurigram's numbering starts at `v2.1.0`, so the pattern can never match one of ours.
#  Reading the reference out of `git` rather than out of PyPI keeps the network off the
#  documentation build; the surface extracted from the resolved commit is identical to the
#  one extracted from the `pyrogram==2.0.106` wheel, across all three packages below.
_REFERENCE_TAG_PATTERN: Final[str] = "v2.0.*"

_GIT: Final[str] = "git"

_PACKAGES: Final[tuple[str, ...]] = ("methods", "types", "enums")

_SCHEMA_PATH: Final[str] = "compiler/api/source/main_api.tl"
_VERSION_PATH: Final[str] = "pyrogram/__init__.py"

_TEMPLATE: Final[Path] = Path("compiler/docs/template/porting.rst")
_DESTINATION: Final[Path] = Path("docs/source/topics/porting-from-pyrogram.rst")

_INDEX: Final[Path] = Path("docs/source/index.rst")
_INDEX_ANCHOR: Final[str] = ":caption: Topic Guides"
_INDEX_ENTRY: Final[str] = "topics/porting-from-pyrogram"

# Every public name the reference exposes and this tree does not. Deriving the list is easy;
#  saying what replaced each one is not, so the prose is written by hand here and the
#  generator refuses to run while any derived name is missing from it. A removal introduced
#  by a later release then breaks `make docs` until somebody writes the sentence, which is
#  the only thing keeping this table from rotting.
_REMOVED: Final[Mapping[str, str]] = {
    "Client.get_nearby_chats": (
        "Removed with no replacement: Telegram retired the nearby-chats feature."
    ),
    "class:ChatPreview": (
        "Merged into :class:`~pyrogram.types.Chat`, which now describes a chat the client "
        "has not joined as well as one it has."
    ),
    "class:InviteLinkImporter": "Renamed to :class:`~pyrogram.types.ChatJoiner`.",
    "Link.format": (
        "Made private: it was the static helper that renders a mention into HTML or "
        "Markdown, and the name now reaches the plain ``str.format``."
    ),
}

# `read` and `write` are Pyrogram's own TL (de)serialization hooks on `Object` subclasses.
#  They are undocumented staticmethods the parser calls, so a porter never writes one, and
#  their parameter renames would otherwise be a third of the "parameters that are gone" table.
_INTERNAL_METHODS: Final[frozenset[str]] = frozenset({"read", "write"})

_ENCODING: Final[str] = "utf-8"


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceRelease:
    version: str
    commit: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Parameter:
    name: str
    default: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Method:
    parameters: tuple[Parameter, ...]

    def names(self) -> tuple[str, ...]:
        return tuple(parameter.name for parameter in self.parameters)

    def default_of(self, name: str) -> str | None:
        for parameter in self.parameters:
            if parameter.name == name:
                return parameter.default

        raise KeyError(name)


@dataclass(frozen=True, slots=True, kw_only=True)
class Surface:
    methods: dict[str, Method] = field(default_factory=dict)
    classes: set[str] = field(default_factory=set)
    enum_members: dict[str, tuple[str, ...]] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)

    def names(self) -> set[str]:
        return set(self.methods) | self.classes


def _parameters(function: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[Parameter, ...]:
    arguments = function.args

    positional = [*arguments.posonlyargs, *arguments.args]
    padding: list[ast.expr | None] = [None] * (len(positional) - len(arguments.defaults))
    positional_defaults = [*padding, *arguments.defaults]

    collected: list[Parameter] = []

    for argument, default in zip(positional, positional_defaults, strict=True):
        if argument.arg != "self":
            collected.append(
                Parameter(
                    name=argument.arg,
                    default=_unparse(default),
                ),
            )

    for argument, default in zip(arguments.kwonlyargs, arguments.kw_defaults, strict=True):
        collected.append(
            Parameter(
                name=argument.arg,
                default=_unparse(default),
            ),
        )

    return tuple(collected)


def _unparse(node: ast.expr | None) -> str | None:
    return None if node is None else ast.unparse(node)


def _enum_members(body: list[ast.stmt]) -> tuple[str, ...]:
    members: list[str] = []

    for statement in body:
        if isinstance(statement, ast.Assign):
            members.extend(
                target.id
                for target in statement.targets
                if isinstance(target, ast.Name) and not target.id.startswith("_")
            )

    return tuple(members)


def _alias_target(statement: ast.stmt) -> tuple[str, str] | None:
    """The `<public name> = <other public name>` pair a statement binds, if it binds one."""
    if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
        return None

    target, value = statement.targets[0], statement.value

    if not isinstance(target, ast.Name) or not isinstance(value, ast.Name):
        return None

    if target.id.startswith("_") or value.id.startswith("_"):
        return None

    return target.id, value.id


def _read_class(*, surface: Surface, node: ast.ClassDef, owner: str | None, is_enum: bool) -> None:
    if owner is None:
        surface.classes.add(f"class:{node.name}")

    # Only a class under `pyrogram/enums` has members. Reading a bare `name = value` in any
    #  other class body as one reported `Message` losing a member when the `reply_text` alias
    #  changed direction.
    if is_enum:
        surface.enum_members[f"class:{node.name}"] = _enum_members(node.body)

    qualifier = owner if owner is not None else node.name

    for statement in node.body:
        alias = _alias_target(statement)

        if alias is not None:
            surface.aliases[f"{qualifier}.{alias[0]}"] = f"{qualifier}.{alias[1]}"

        if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        if not statement.name.startswith("_") and statement.name not in _INTERNAL_METHODS:
            surface.methods[f"{qualifier}.{statement.name}"] = Method(
                parameters=_parameters(statement),
            )


def _read_module(*, surface: Surface, source: str, path: str) -> None:
    # A class under `pyrogram/methods` is a mixin `Client` inherits, not a public name, and
    #  nobody calls `SendPoll.send_poll`. So its methods are recorded under `Client` and the
    #  mixin itself is not recorded at all: it would otherwise report `SendCode` as a removed
    #  type when the method it carried was merely renamed.
    package = Path(path).parts[1]

    owner = "Client" if package == "methods" else None

    module = ast.parse(source, filename=path)

    for node in module.body:
        alias = _alias_target(node)

        if alias is not None and owner is None:
            surface.aliases[f"class:{alias[0]}"] = f"class:{alias[1]}"

        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            _read_class(
                surface=surface,
                node=node,
                owner=owner,
                is_enum=package == "enums",
            )


def _resolve_reference() -> ReferenceRelease:
    """The last Pyrogram release, resolved from this repository's own tags."""
    tags = subprocess.run(
        [_GIT, "tag", "--list", _REFERENCE_TAG_PATTERN, "--sort=version:refname"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.split()

    if not tags:
        raise SystemExit(
            f"no tag matches `{_REFERENCE_TAG_PATTERN}`, so the reference release cannot be "
            "resolved. A shallow or `--no-tags` clone is the usual cause: fetch the tags "
            "(`git fetch --tags`) and rerun."
        )

    tag = tags[-1]

    commit = subprocess.run(
        [_GIT, "rev-parse", f"{tag}^{{}}"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()

    return ReferenceRelease(
        version=tag.removeprefix("v"),
        commit=commit,
    )


def _read_reference(commit: str) -> Surface:
    """The reference surface, streamed straight out of `git archive`."""
    archive = subprocess.run(
        [_GIT, "archive", commit, *(f"pyrogram/{name}" for name in _PACKAGES)],
        capture_output=True,
        check=True,
    ).stdout

    surface = Surface()

    with tarfile.open(
        fileobj=io.BytesIO(archive),
        mode="r",
    ) as bundle:
        for member in bundle.getmembers():
            if not member.name.endswith(".py"):
                continue

            handle = bundle.extractfile(member)

            if handle is not None:
                _read_module(
                    surface=surface,
                    source=handle.read().decode(_ENCODING),
                    path=member.name,
                )

    return surface


def _read_tree() -> Surface:
    surface = Surface()

    for package in _PACKAGES:
        for path in sorted(Path("pyrogram", package).rglob("*.py")):
            _read_module(
                surface=surface,
                source=path.read_text(encoding=_ENCODING),
                path=str(path),
            )

    return surface


def _git_show(*, commit: str, path: str) -> str:
    return subprocess.run(
        [_GIT, "show", f"{commit}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout


def _layer_of(source: str) -> str:
    for line in source.splitlines():
        if line.startswith("// LAYER "):
            return line.removeprefix("// LAYER ").strip()

    raise ValueError("no `// LAYER` line in the schema")


def _version_of(source: str) -> str:
    for line in source.splitlines():
        if line.startswith("__version__"):
            return line.split("=", maxsplit=1)[1].strip().strip('"')

    raise ValueError("no `__version__` line")


def _table(*, headers: tuple[str, str], rows: list[tuple[str, str]]) -> str:
    """An RST list-table, which needs no column arithmetic and wraps long cells by itself."""
    if not rows:
        return "None.\n"

    lines = [
        ".. list-table::",
        "    :header-rows: 1",
        "    :widths: 30 70",
        "",
        f"    * - {headers[0]}",
        f"      - {headers[1]}",
    ]

    for left, right in rows:
        lines.append(f"    * - {left}")
        lines.append(f"      - {right}")

    return "\n".join(lines) + "\n"


def _render_removed(*, reference: Surface, here: Surface) -> str:
    gone = sorted(reference.names() - here.names() - set(here.aliases))

    undocumented = [name for name in gone if name not in _REMOVED]

    if undocumented:
        raise SystemExit(
            "These public names are gone from this tree and `_REMOVED` in "
            f"`{__file__}` does not say what replaced them: {undocumented}"
        )

    rows = [(f"``{name.removeprefix('class:')}``", _REMOVED[name]) for name in gone]

    return _table(
        headers=("Gone from Kurigram", "What to write instead"),
        rows=rows,
    )


def _render_dropped_parameters(*, reference: Surface, here: Surface) -> str:
    rows: list[tuple[str, str]] = []

    for name in sorted(set(reference.methods) & set(here.methods)):
        dropped = [
            parameter
            for parameter in reference.methods[name].names()
            if parameter not in here.methods[name].names()
        ]

        if dropped:
            rows.append((f"``{name}``", ", ".join(f"``{item}``" for item in dropped)))

    return _table(
        headers=("Method", "Parameters it no longer accepts"),
        rows=rows,
    )


def _render_aliases(*, reference: Surface, here: Surface) -> str:
    rows: list[tuple[str, str]] = []

    for name in sorted(reference.names()):
        if name in here.names():
            continue

        target = here.aliases.get(name)

        if target is not None:
            rows.append(
                (
                    f"``{name.removeprefix('class:')}``",
                    f"``{target.removeprefix('class:')}``",
                )
            )

    return _table(
        headers=("Pyrogram name", "What it is an alias of"),
        rows=rows,
    )


def _render_positional(*, reference: Surface, here: Surface) -> str:
    rows: list[tuple[str, str]] = []

    for name in sorted(set(reference.methods) & set(here.methods)):
        before = reference.methods[name].names()
        after = here.methods[name].names()

        shared_length = min(len(before), len(after))

        # Parameters appended after the last of Pyrogram's own never move an existing
        #  argument, so a method only lands in this table when a position a Pyrogram call
        #  could actually have filled now holds something else.
        safe = next(
            (index for index in range(shared_length) if before[index] != after[index]),
            shared_length,
        )

        # A fully-equal shared prefix cannot misbind: what the tree APPENDED moves nothing,
        #  and a DROPPED tail makes an over-full positional call raise `TypeError`, which the
        #  parameters table already covers. Indexing `after[safe]` in the dropped-tail case
        #  was also an `IndexError` waiting for the first release that produces one.
        if safe >= shared_length:
            continue

        rows.append(
            (
                f"``{name}``",
                (
                    f"the first {safe} still bind the same way; argument {safe + 1} was "
                    f"``{before[safe]}`` and is now ``{after[safe]}``"
                ),
            )
        )

    return _table(
        headers=("Method", "How far a positional call is still safe"),
        rows=rows,
    )


def _render_defaults(*, reference: Surface, here: Surface) -> str:
    rows: list[tuple[str, str]] = []

    for name in sorted(set(reference.methods) & set(here.methods)):
        for parameter in reference.methods[name].names():
            if parameter not in here.methods[name].names():
                continue

            before = reference.methods[name].default_of(parameter)
            after = here.methods[name].default_of(parameter)

            if before == after:
                continue

            # A parameter that merely GAINED a default cannot break an existing call, so
            #  listing it is noise. One that LOST its default now raises `TypeError` when
            #  omitted, and rendering that as ``None`` to ``None`` read as no change at all:
            #  the extractor uses `None` for "no default", which prints like a `None` default.
            if before is None:
                continue

            if after is None:
                rows.append((f"``{name}``", f"``{parameter}``: had ``{before}``, now required"))

            else:
                rows.append((f"``{name}``", f"``{parameter}``: ``{before}`` to ``{after}``"))

    return _table(
        headers=("Method", "Default that changed"),
        rows=rows,
    )


def _render_enum_members(*, reference: Surface, here: Surface) -> str:
    rows: list[tuple[str, str]] = []

    for name in sorted(set(reference.enum_members) & set(here.enum_members)):
        dropped = [
            member
            for member in reference.enum_members[name]
            if member not in here.enum_members[name]
        ]

        if dropped:
            rows.append(
                (
                    f"``{name.removeprefix('class:')}``",
                    ", ".join(f"``{member}``" for member in dropped),
                )
            )

    return _table(
        headers=("Enumeration", "Members it no longer has"),
        rows=rows,
    )


def _counts(*, reference: Surface, here: Surface) -> dict[str, int]:
    added: set[str] = set(here.methods) - set(reference.methods)
    new_enums: set[str] = set(here.enum_members) - set(reference.enum_members)

    return {
        "reference_methods": len(reference.methods),
        "tree_methods": len(here.methods),
        "added_methods": len(added),
        "reference_enums": len(reference.enum_members),
        "tree_enums": len(here.enum_members),
        "added_enums": len(new_enums),
    }


def _wire_into_toctree() -> None:
    lines = _INDEX.read_text(encoding=_ENCODING).splitlines()

    if any(line.strip() == _INDEX_ENTRY for line in lines):
        return

    for position, line in enumerate(lines):
        if line.strip() != _INDEX_ANCHOR:
            continue

        # The caption is the last option of the directive, so the entries start after the
        #  blank line that closes the option block.
        insertion: int = position + 2
        lines.insert(insertion, f"    {_INDEX_ENTRY}")

        _INDEX.write_text("\n".join(lines) + "\n", encoding=_ENCODING)
        return

    raise SystemExit(
        f"`{_INDEX}` has no `{_INDEX_ANCHOR}` toctree, so the porting guide would build as "
        "an orphan page. Add the toctree back, or point `_INDEX_ANCHOR` at its replacement."
    )


def start() -> None:
    release = _resolve_reference()

    reference = _read_reference(release.commit)
    here = _read_tree()

    page = _TEMPLATE.read_text(encoding=_ENCODING).format(
        reference_version=release.version,
        reference_commit=release.commit[:8],
        reference_layer=_layer_of(
            _git_show(
                commit=release.commit,
                path=_SCHEMA_PATH,
            ),
        ),
        tree_version=_version_of(Path(_VERSION_PATH).read_text(encoding=_ENCODING)),
        tree_layer=_layer_of(Path(_SCHEMA_PATH).read_text(encoding=_ENCODING)),
        removed=_render_removed(
            reference=reference,
            here=here,
        ),
        aliases=_render_aliases(
            reference=reference,
            here=here,
        ),
        dropped_parameters=_render_dropped_parameters(
            reference=reference,
            here=here,
        ),
        positional=_render_positional(
            reference=reference,
            here=here,
        ),
        defaults=_render_defaults(
            reference=reference,
            here=here,
        ),
        enum_members=_render_enum_members(
            reference=reference,
            here=here,
        ),
        **_counts(
            reference=reference,
            here=here,
        ),
    )

    _DESTINATION.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    _DESTINATION.write_text(page, encoding=_ENCODING)

    _wire_into_toctree()

    print(f"porting guide written to {_DESTINATION}", file=sys.stderr)


if "__main__" == __name__:
    start()

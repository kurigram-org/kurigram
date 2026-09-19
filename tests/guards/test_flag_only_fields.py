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

"""`value or None` on a `flags.N?true` field writes the same bytes as `value`.

Such a field has no payload at all: the flag bit IS the value, and the generated writer
decides the bit with a plain truthiness test, so `False` and `None` are indistinguishable
on the wire. The `or None` then reads as a guard and guards nothing.

Every other optional field is the opposite case and must keep passing. `flags.N?Bool`,
`flags.N?string` and `flags.N?Vector<T>` carry their value separately from the bit, so
`or None` there decides what reaches the server - an explicit `BoolFalse` or an omitted
field, an empty string or no string at all.

Which of the two a call site is cannot be read off the call site. It is read off the
schema, by the constructor's name, which is why this walks the tree and `main_api.tl`
together rather than keeping a list.
"""

from __future__ import annotations as _annotations

import ast
import re
from dataclasses import dataclass
from typing import Final, TYPE_CHECKING

from compiler.api.compiler import ARGS_RE, COMBINATOR_RE, SECTION_RE, camel
from tests.guards.name_resolution import REPOSITORY_ROOT, hand_written_files

if TYPE_CHECKING:
    from collections.abc import Iterator
    import pathlib

_SCHEMA_ROOT: Final[pathlib.Path] = REPOSITORY_ROOT / "compiler" / "api" / "source"

# The three files `compiler/api/compiler.py` concatenates before it parses them. Only
#  `main_api.tl` declares a `?true` field, but the handshake constructors come from the
#  other two and have to resolve as well, or a site that uses one reads as unclassifiable.
_SCHEMA_FILES: Final[tuple[str, ...]] = ("auth_key.tl", "sys_msgs.tl", "main_api.tl")

_FLAG_ONLY_RE: Final[re.Pattern[str]] = re.compile(r"^flags\d?\.\d+\?true$")

# The two TL field names that are Python keywords. `compiler/api/compiler.py` renames them
#  where it emits the parameters, so a call site spells them this way; `user`,
#  `channelParticipantAdmin` and `groupCallParticipant` all declare `self:flags.N?true`,
#  so an index that skipped the rename would be blind to three of the fields this guards.
_RENAMED_FIELDS: Final[dict[str, str]] = {"self": "is_self", "from": "from_peer"}

# The two generated namespaces that hold constructors. `raw.base` holds the abstract types
#  and `raw.core` the hand-written primitives, and neither is ever called.
_SECTIONS: Final[tuple[str, ...]] = ("types", "functions")

# What the two self-tests below run the classifier over: both routes to a constructor, a
#  `?true` field, a chained `or`, a renamed field, three fields that are optional but carry
#  a payload, and four forms that are not an `or None` on a constructor keyword at all.
_SAMPLE_CALLS: Final[str] = (
    "from pyrogram.raw.types import DocumentAttributeVideo\n"
    "DocumentAttributeVideo(round_message=value or None)\n"
    "raw.types.DocumentAttributeVideo(supports_streaming=value or None)\n"
    "raw.types.InputMediaUploadedDocument(force_file=first or second or None)\n"
    "raw.types.User(is_self=value or None)\n"
    "raw.types.ReplyKeyboardMarkup(placeholder=value or None)\n"
    "raw.functions.messages.SendMedia(entities=value or None)\n"
    "raw.types.InputMediaUploadedDocument(mime_type=value or None)\n"
    "raw.types.InputMediaUploadedDocument(force_file=value)\n"
    "raw.types.InputMediaUploadedDocument(force_file=None or value)\n"
    "other.types.InputMediaUploadedDocument(force_file=value or None)\n"
    "raw.types.DocumentAttributeVideo(**{'supports_streaming': value or None})\n"
)


@dataclass(frozen=True, slots=True)
class OrNoneSite:
    """One `<expr> or None` keyword argument of a `raw.*` constructor call."""

    path: str
    line: int
    constructor: str
    field: str

    def described(self, *, declared: str) -> str:
        return f"{self.path}:{self.line}: raw.{self.constructor}.{self.field} is `{declared}`"


def schema_fields() -> dict[str, dict[str, str]]:
    """Every TL constructor, keyed by the `raw.` path that reaches it, mapped to its fields."""
    index: dict[str, dict[str, str]] = {}
    section: str = ""

    for name in _SCHEMA_FILES:
        for line in (_SCHEMA_ROOT / name).read_text(encoding="utf-8").splitlines():
            section_match = SECTION_RE.match(line)

            if section_match:
                section = section_match.group(1)
                continue

            combinator_match = COMBINATOR_RE.match(line)

            if combinator_match is None:
                continue

            namespace, _, bare = combinator_match.group(1).rpartition(".")
            qualified = f"{namespace}.{camel(bare)}" if namespace else camel(bare)

            index[f"{section}.{qualified}"] = {
                _RENAMED_FIELDS.get(field, field): declared
                for field, declared in ARGS_RE.findall(line)
            }

    return index


def attribute_chain(node: ast.expr) -> list[str]:
    """`raw.types.Foo` read as `["raw", "types", "Foo"]`, and anything else as nothing."""
    parts: list[str] = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if not isinstance(node, ast.Name):
        return []

    parts.append(node.id)

    return list(reversed(parts))


def ends_in_none(node: ast.expr) -> bool:
    """Whether the value is an `or` chain whose last operand is the `None` literal."""
    if not isinstance(node, ast.BoolOp) or not isinstance(node.op, ast.Or):
        return False

    last = node.values[-1]

    return isinstance(last, ast.Constant) and last.value is None


def imported_constructors(tree: ast.AST) -> dict[str, str]:
    """Local name -> constructor path, for the `from pyrogram.raw.<section> import Name` form.

    `pyrogram/session/internals/msg_factory.py` writes `Ping(...)` that way, so a walk that
    only followed the `raw.` namespace would be blind to a whole module rather than to a line.
    """
    bound: dict[str, str] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module is None:
            continue

        inside_raw = node.module.removeprefix("pyrogram.raw.")

        if inside_raw == node.module or inside_raw.split(".")[0] not in _SECTIONS:
            continue

        for alias in node.names:
            bound[alias.asname or alias.name] = f"{inside_raw}.{alias.name}"

    return bound


def called_constructor(node: ast.Call, *, imported: dict[str, str]) -> str:
    """The constructor path a call reaches, or nothing when the call is not a constructor."""
    chain = attribute_chain(node.func)

    if len(chain) >= 3 and chain[0] == "raw":
        return ".".join(chain[1:])

    if len(chain) == 1:
        return imported.get(chain[0], "")

    return ""


def or_none_sites(tree: ast.AST, *, path: str) -> Iterator[OrNoneSite]:
    imported = imported_constructors(tree)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        constructor = called_constructor(node, imported=imported)

        if not constructor:
            continue

        for keyword in node.keywords:
            if keyword.arg is not None and ends_in_none(keyword.value):
                yield OrNoneSite(
                    path=path,
                    line=keyword.value.lineno,
                    constructor=constructor,
                    field=keyword.arg,
                )


def package_or_none_sites() -> list[OrNoneSite]:
    found: list[OrNoneSite] = []

    for path in hand_written_files():
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)

        found.extend(or_none_sites(tree, path=relative))

    return found


def raw_bound_under_another_name(tree: ast.AST) -> Iterator[str]:
    """Import forms that would put a constructor call beyond both routes `or_none_sites` follows."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names if alias.name.startswith("pyrogram.raw"))

        if not isinstance(node, ast.ImportFrom) or node.module is None:
            continue

        if node.module == "pyrogram":
            yield from (
                f"raw as {alias.asname}"
                for alias in node.names
                if alias.name == "raw" and alias.asname is not None
            )

        elif node.module == "pyrogram.raw":
            yield from (
                f"pyrogram.raw.{alias.name}" for alias in node.names if alias.name in _SECTIONS
            )


def declared_type(site: OrNoneSite, *, schema: dict[str, dict[str, str]]) -> str | None:
    fields = schema.get(site.constructor)

    return None if fields is None else fields.get(site.field)


def test_no_or_none_reaches_a_flag_only_field() -> None:
    schema = schema_fields()

    offenders = [
        site.described(declared=declared)
        for site in package_or_none_sites()
        if (declared := declared_type(site, schema=schema)) is not None
        and _FLAG_ONLY_RE.match(declared)
    ]

    assert offenders == []


def test_every_or_none_site_resolves_to_a_declared_field() -> None:
    """A renamed constructor or field would otherwise switch the guard above off in silence."""
    schema = schema_fields()

    unresolved = [
        f"{site.path}:{site.line}: raw.{site.constructor} declares no `{site.field}`"
        for site in package_or_none_sites()
        if declared_type(site, schema=schema) is None
    ]

    assert unresolved == []


def test_no_module_binds_the_raw_namespace_under_another_name() -> None:
    """The third import form, which neither route follows and which the package does not use."""
    bound = [
        f"{path.relative_to(REPOSITORY_ROOT).as_posix()}: {name}"
        for path in hand_written_files()
        for name in raw_bound_under_another_name(ast.parse(path.read_text()))
    ]

    assert bound == []


def test_the_schema_index_loses_no_constructor() -> None:
    """Two combinators camel-casing to one name would drop a constructor out of the index."""
    declared = sum(
        1
        for name in _SCHEMA_FILES
        for line in (_SCHEMA_ROOT / name).read_text(encoding="utf-8").splitlines()
        if COMBINATOR_RE.match(line)
    )

    assert len(schema_fields()) == declared


def test_the_sweep_reads_the_call_forms_it_claims_to() -> None:
    schema = schema_fields()

    classified = {
        f"{site.constructor}.{site.field}": declared_type(site, schema=schema)
        for site in or_none_sites(ast.parse(_SAMPLE_CALLS), path="<sample>")
    }

    assert classified == {
        "types.DocumentAttributeVideo.round_message": "flags.0?true",
        "types.DocumentAttributeVideo.supports_streaming": "flags.1?true",
        "types.InputMediaUploadedDocument.force_file": "flags.4?true",
        "types.User.is_self": "flags.10?true",
        "types.ReplyKeyboardMarkup.placeholder": "flags.3?string",
        "functions.messages.SendMedia.entities": "flags.3?Vector<MessageEntity>",
        "types.InputMediaUploadedDocument.mime_type": "string",
    }


def test_only_a_flag_only_field_is_an_offender() -> None:
    schema = schema_fields()

    offenders = sorted(
        f"{site.constructor}.{site.field}"
        for site in or_none_sites(ast.parse(_SAMPLE_CALLS), path="<sample>")
        if (declared := declared_type(site, schema=schema)) is not None
        and _FLAG_ONLY_RE.match(declared)
    )

    assert offenders == [
        "types.DocumentAttributeVideo.round_message",
        "types.DocumentAttributeVideo.supports_streaming",
        "types.InputMediaUploadedDocument.force_file",
        "types.User.is_self",
    ]

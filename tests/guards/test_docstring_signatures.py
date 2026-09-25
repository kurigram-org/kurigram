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

"""Every `Parameters:` block says what its own signature says.

A documented parameter the signature does not carry sends the reader to a keyword that raises
`TypeError`, and a parameter with no entry is invisible: the reference pages are generated from
these blocks, so whatever is missing here is missing everywhere. Neither Sphinx nor the type
checker compares the two, because to both of them a docstring is an opaque string.

The `*optional*` marker is the same question asked of one entry: it is this tree's way of saying
the parameter has a default, so a marker that disagrees with the signature is a promise the
caller cannot keep either way round.
"""

from __future__ import annotations as _annotations

import ast
import dataclasses
import pathlib
import re
from typing import Final, TYPE_CHECKING
from re import Pattern

from tests.guards.name_resolution import REPOSITORY_ROOT, hand_written_files

if TYPE_CHECKING:
    from collections.abc import Iterator

# An entry reads `    reply_markup (``InlineKeyboardMarkup``, *optional*):`: the name, then
#  the type and the markers in brackets, then the colon that makes Sphinx render the line as
#  a definition term. The stars belong to `*args` and `**kwargs` and are not part of the
#  name. An entry written without the colon is read as absent, so its parameter is reported
#  as undocumented, which is what enforces the colon.
_ENTRY: Final[Pattern[str]] = re.compile(r"^(?P<indent> *)\*{0,2}(?P<name>\w+) \((?P<spec>.*)\):$")

_OPTIONAL_MARKER: Final[str] = "*optional*"

_BLOCK_HEADING: Final[str] = "Parameters:"

# An entry sits one level in from the heading; anything deeper is the description under one.
_ENTRY_INDENT: Final[int] = 4

_RECEIVERS: Final[frozenset[str]] = frozenset({"self", "cls"})

# Whole modules another branch is rewriting. Editing a docstring in one of them conflicts with
#  work already in review, so their drift is left for that branch to carry. Drop an entry once
#  its branch lands; `test_every_exemption_still_names_a_module_that_drifts` fails on one that
#  has nothing left to exempt.
_HELD_BY_A_PULL_REQUEST: Final[dict[str, str]] = {}


@dataclasses.dataclass(frozen=True, slots=True)
class DocumentedParameter:
    name: str
    line: int
    marked_optional: bool


@dataclasses.dataclass(frozen=True, slots=True)
class DocumentedFunction:
    module: str
    node: ast.FunctionDef | ast.AsyncFunctionDef
    documented: list[DocumentedParameter]


@dataclasses.dataclass(frozen=True, slots=True)
class Drift:
    module: str
    line: int
    function: str
    complaint: str

    def __str__(self) -> str:
        return f"{self.module}:{self.line}: {self.function}: {self.complaint}"


def documented_parameters(*, lines: list[str], first_line: int) -> list[DocumentedParameter]:
    """Read the `Parameters:` block out of the raw source lines of one docstring.

    The raw lines rather than `ast.get_docstring`, because the entries are told apart from
    their own descriptions by indentation and `inspect.cleandoc` moves it.
    """
    heading: int | None = next(
        (offset for offset, line in enumerate(lines) if line.strip() == _BLOCK_HEADING),
        None,
    )

    if heading is None:
        return []

    base: int = len(lines[heading]) - len(lines[heading].lstrip())
    found: list[DocumentedParameter] = []

    for offset, line in enumerate(lines[heading + 1 :], start=heading + 1):
        if line.strip() and len(line) - len(line.lstrip()) <= base:
            break

        entry = _ENTRY.match(line.rstrip())

        if entry is None or len(entry["indent"]) != base + _ENTRY_INDENT:
            continue

        found.append(
            DocumentedParameter(
                name=entry["name"],
                line=first_line + offset,
                marked_optional=_OPTIONAL_MARKER in entry["spec"],
            )
        )

    return found


def signature_parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, bool]:
    """Every parameter of `node`, mapped to whether a caller may leave it out."""
    arguments = node.args
    positional: list[ast.arg] = arguments.posonlyargs + arguments.args
    omittable: dict[str, bool] = {parameter.arg: False for parameter in positional}

    for parameter, _ in zip(reversed(positional), reversed(arguments.defaults), strict=False):
        omittable[parameter.arg] = True

    for parameter, default in zip(arguments.kwonlyargs, arguments.kw_defaults, strict=True):
        omittable[parameter.arg] = default is not None

    # `*args` and `**kwargs` carry no default and are omittable regardless, so the marker on
    #  one of them is right either way.
    for collector in (arguments.vararg, arguments.kwarg):
        if collector is not None:
            omittable[collector.arg] = True

    for receiver in _RECEIVERS:
        omittable.pop(receiver, None)

    return omittable


def documented_functions() -> Iterator[DocumentedFunction]:
    """Every function of the package whose docstring carries a `Parameters:` block."""
    for path in hand_written_files():
        module = path.relative_to(REPOSITORY_ROOT).as_posix()
        source = path.read_text(encoding="utf-8").splitlines()

        for node in ast.walk(ast.parse("\n".join(source), filename=module)):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if ast.get_docstring(node) is None:
                continue

            literal = node.body[0].value
            lines = source[literal.lineno - 1 : literal.end_lineno]
            documented = documented_parameters(
                lines=lines,
                first_line=literal.lineno,
            )

            if documented:
                yield DocumentedFunction(
                    module=module,
                    node=node,
                    documented=documented,
                )


def name_drift() -> list[Drift]:
    """Every entry naming something the signature does not have, and every parameter with none."""
    found: list[Drift] = []

    for found_function in documented_functions():
        omittable = signature_parameters(found_function.node)
        written = {parameter.name for parameter in found_function.documented}

        for parameter in found_function.documented:
            if parameter.name not in omittable:
                found.append(
                    Drift(
                        module=found_function.module,
                        line=parameter.line,
                        function=found_function.node.name,
                        complaint=f"`{parameter.name}` is not a parameter",
                    )
                )

        for name in sorted(set(omittable) - written):
            found.append(
                Drift(
                    module=found_function.module,
                    line=found_function.node.lineno,
                    function=found_function.node.name,
                    complaint=f"`{name}` has no entry",
                )
            )

    return found


def marker_drift() -> list[Drift]:
    """Every `*optional*` marker that disagrees with whether the parameter has a default."""
    found: list[Drift] = []

    for found_function in documented_functions():
        omittable = signature_parameters(found_function.node)

        for parameter in found_function.documented:
            if parameter.name not in omittable:
                continue

            if parameter.marked_optional == omittable[parameter.name]:
                continue

            complaint = (
                f"`{parameter.name}` is marked optional and has no default"
                if parameter.marked_optional
                else f"`{parameter.name}` has a default and is not marked optional"
            )
            found.append(
                Drift(
                    module=found_function.module,
                    line=parameter.line,
                    function=found_function.node.name,
                    complaint=complaint,
                )
            )

    return found


def free_of_an_open_pull_request(drifts: list[Drift]) -> list[str]:
    return sorted(str(drift) for drift in drifts if drift.module not in _HELD_BY_A_PULL_REQUEST)


def test_every_documented_parameter_is_a_parameter_and_every_parameter_is_documented() -> None:
    disagreeing = free_of_an_open_pull_request(name_drift())

    assert not disagreeing, "{} documented names disagree with their signature:\n{}".format(
        len(disagreeing),
        "\n".join(disagreeing),
    )


def test_every_optional_marker_agrees_with_the_default() -> None:
    disagreeing = free_of_an_open_pull_request(marker_drift())

    assert not disagreeing, "{} markers disagree with their default:\n{}".format(
        len(disagreeing),
        "\n".join(disagreeing),
    )


def test_every_exemption_still_names_a_module_that_drifts() -> None:
    """An exemption whose pull request has merged silences a file that is now free."""
    drifting = {drift.module for drift in name_drift() + marker_drift()}
    stale = sorted(set(_HELD_BY_A_PULL_REQUEST) - drifting)

    assert not stale, "{} exemptions have nothing left to exempt:\n{}".format(
        len(stale),
        "\n".join(stale),
    )


def test_every_exemption_names_a_module_that_exists() -> None:
    missing = sorted(
        module for module in _HELD_BY_A_PULL_REQUEST if not (REPOSITORY_ROOT / module).is_file()
    )

    assert missing == []


def test_the_sweep_reads_the_blocks_it_claims_to() -> None:
    """A regex that stopped matching would leave both rules above passing over nothing."""
    blocks = {found.module: found.documented for found in documented_functions()}

    assert len(blocks) > 200
    assert "pyrogram/methods/messages/send_message.py" in blocks

    documented = {
        parameter.name for parameter in blocks["pyrogram/methods/messages/send_message.py"]
    }

    assert {"chat_id", "text", "parse_mode", "reply_markup"} <= documented


def test_the_sweep_reads_an_entry_and_skips_its_description() -> None:
    lines = [
        '"""Send a message.',
        "",
        "        Parameters:",
        "            chat_id (``int`` | ``str``):",
        "                Unique identifier of the target chat.",
        "                Written as ``name (type):`` and still prose.",
        "",
        "            reply_markup (``InlineKeyboardMarkup``, *optional*):",
        "                An interface.",
        "",
        "            **kwargs (``any``, *optional*):",
        "                Anything else.",
        "",
        "            colon_less (``int``, *optional*)",
        "                Written without the closing colon, so read as absent.",
        "",
        "        Returns:",
        "            not_a_parameter (``int``):",
        '        """',
    ]

    read = documented_parameters(
        lines=lines,
        first_line=1,
    )

    assert read == [
        DocumentedParameter(name="chat_id", line=4, marked_optional=False),
        DocumentedParameter(name="reply_markup", line=8, marked_optional=True),
        DocumentedParameter(name="kwargs", line=11, marked_optional=True),
    ]


def test_the_sweep_reads_the_defaults_it_claims_to() -> None:
    source: str = (
        "def f(self, required, defaulted=1, *args, keyword_only, keyword_defaulted=2, **kwargs):"
        " ...\n"
    )
    node = ast.parse(source).body[0]

    assert signature_parameters(node) == {
        "required": False,
        "defaulted": True,
        "args": True,
        "keyword_only": False,
        "keyword_defaulted": True,
        "kwargs": True,
    }


def test_a_module_outside_the_package_is_not_swept() -> None:
    modules = {found.module for found in documented_functions()}

    assert pathlib.Path(__file__).name not in {pathlib.Path(module).name for module in modules}

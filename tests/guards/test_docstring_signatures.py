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
    from collections.abc import Generator

# An entry reads `    reply_markup (``InlineKeyboardMarkup``, *optional*):`: the name, then
#  the type and the markers in brackets, then the colon that makes Sphinx render the line as
#  a definition term. The stars belong to `*args` and `**kwargs` and are not part of the
#  name. An entry written without the colon is read as absent, so its parameter is reported
#  as undocumented, which is what enforces the colon.
_ENTRY: Final[Pattern[str]] = re.compile(r"^(?P<indent> *)\*{0,2}(?P<name>\w+) \((?P<spec>.*)\):$")

_OPTIONAL_MARKER: Final[str] = "*optional*"

# A class block also lists its properties, marked so; they are attributes, not parameters.
_PROPERTY_MARKER: Final[str] = "*property*"

_BLOCK_HEADING: Final[str] = "Parameters:"

# An entry sits one level in from the heading; anything deeper is the description under one.
_ENTRY_INDENT: Final[int] = 4

_RECEIVERS: Final[frozenset[str]] = frozenset({"self", "cls"})

# Every type takes the client that parsed it, to back its bound methods; no type documents it.
_CONSTRUCTOR_WIRING: Final[frozenset[str]] = frozenset({"client"})

_PARSE_REWRITE: Final[str] = "in review: every `_parse` raises on an empty constructor"
_AIOFILES: Final[str] = "in review: local file I/O moves to `aiofiles`"
_SESSION_HARDENING: Final[str] = "in review: session survives an unknown constructor"
_CHAT_ACTIONS: Final[str] = "in review: emoji-interaction chat actions"

# Whole modules a docstring edit here cannot fix, each with why: a branch in review rewrites it,
#  so an edit would conflict, or the fix is a code change. Drop an entry once that lands;
#  `test_every_exemption_still_names_a_module_that_drifts` fails on one with nothing to exempt.
_EXEMPT: Final[dict[str, str]] = {
    "pyrogram/client.py": f"{_AIOFILES}; {_SESSION_HARDENING}",
    "pyrogram/types/bots_and_keyboards/callback_query.py": _PARSE_REWRITE,
    "pyrogram/types/bots_and_keyboards/message_reaction_updated.py": _PARSE_REWRITE,
    "pyrogram/types/inline_mode/inline_query.py": _PARSE_REWRITE,
    "pyrogram/types/input_content/input_chat_photo.py": _AIOFILES,
    "pyrogram/types/input_content/input_media_animation.py": _AIOFILES,
    "pyrogram/types/input_content/input_media_audio.py": _AIOFILES,
    "pyrogram/types/input_content/input_media_document.py": _AIOFILES,
    "pyrogram/types/input_content/input_media_live_photo.py": _AIOFILES,
    "pyrogram/types/input_content/input_media_photo.py": _AIOFILES,
    "pyrogram/types/input_content/input_media_video.py": _AIOFILES,
    "pyrogram/types/input_content/input_media_voice_note.py": _AIOFILES,
    "pyrogram/types/messages_and_media/external_reply_info.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/forum_topic.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/gifted_grams.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/gifted_premium.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/gifted_stars.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/giveaway.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/giveaway_prize_stars.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/giveaway_winners.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/media_area.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/message.py": f"{_AIOFILES}; {_CHAT_ACTIONS}; {_PARSE_REWRITE}",
    "pyrogram/types/messages_and_media/message_content.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/message_origin_import.py": (
        "documents `type`, which its `__init__` does not take: a signature change"
    ),
    "pyrogram/types/messages_and_media/story.py": f"{_AIOFILES}; {_PARSE_REWRITE}",
    "pyrogram/types/messages_and_media/successful_payment.py": _PARSE_REWRITE,
    "pyrogram/types/messages_and_media/web_page.py": _PARSE_REWRITE,
    "pyrogram/types/user_and_chats/chat_folder_invite_link_info.py": _PARSE_REWRITE,
    "pyrogram/types/user_and_chats/chat_invite_link.py": _PARSE_REWRITE,
    "pyrogram/types/user_and_chats/chat_permissions.py": _PARSE_REWRITE,
    "pyrogram/types/user_and_chats/community.py": _PARSE_REWRITE,
    "pyrogram/types/user_and_chats/user.py": _PARSE_REWRITE,
}


@dataclasses.dataclass(frozen=True, slots=True)
class DocumentedParameter:
    name: str
    line: int
    marked_optional: bool


@dataclasses.dataclass(frozen=True, slots=True)
class DocumentedFunction:
    """A `Parameters:` block and the signature it describes.

    A class documents its constructor, so its block is held against `__init__`.
    """

    module: str
    name: str
    line: int
    omittable: dict[str, bool]
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

        if _PROPERTY_MARKER in entry["spec"]:
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


def constructor(node: ast.ClassDef) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    return next(
        (
            statement
            for statement in node.body
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
            and statement.name == "__init__"
        ),
        None,
    )


def omittable_parameters(
    *,
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    module: str,
) -> dict[str, bool]:
    """What the block of `node` is held against: its own signature, or its class's `__init__`."""
    if not isinstance(node, ast.ClassDef):
        return signature_parameters(node)

    signature = constructor(node)

    # An inherited `__init__` would need the import resolved; no class does this yet.
    assert signature is not None, (
        f"{module}:{node.lineno}: {node.name} documents parameters and defines no `__init__`"
    )

    omittable = signature_parameters(signature)

    for wiring in _CONSTRUCTOR_WIRING:
        omittable.pop(wiring, None)

    return omittable


def documented_blocks(*, module: str, source: list[str]) -> Generator[DocumentedFunction]:
    """Every function and class in `source` whose docstring carries a `Parameters:` block."""
    for node in ast.walk(ast.parse("\n".join(source), filename=module)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        if ast.get_docstring(node) is None:
            continue

        literal = node.body[0].value
        documented = documented_parameters(
            lines=source[literal.lineno - 1 : literal.end_lineno],
            first_line=literal.lineno,
        )

        if not documented:
            continue

        yield DocumentedFunction(
            module=module,
            name=node.name,
            line=node.lineno,
            omittable=omittable_parameters(
                node=node,
                module=module,
            ),
            documented=documented,
        )


def documented_functions() -> Generator[DocumentedFunction]:
    """Every `Parameters:` block of the package, with the signature it describes."""
    for path in hand_written_files():
        yield from documented_blocks(
            module=path.relative_to(REPOSITORY_ROOT).as_posix(),
            source=path.read_text(encoding="utf-8").splitlines(),
        )


def block_name_drift(found_function: DocumentedFunction) -> list[Drift]:
    """Every entry naming a non-parameter or a name already documented, and every parameter with none."""
    omittable = found_function.omittable
    found: list[Drift] = []
    written: set[str] = set()

    for parameter in found_function.documented:
        complaint: str | None = None

        if parameter.name in written:
            complaint = f"`{parameter.name}` is documented twice"
        elif parameter.name not in omittable:
            complaint = f"`{parameter.name}` is not a parameter"

        written.add(parameter.name)

        if complaint is None:
            continue

        drift = Drift(
            module=found_function.module,
            line=parameter.line,
            function=found_function.name,
            complaint=complaint,
        )
        found.append(drift)

    for name in sorted(set(omittable) - written):
        drift = Drift(
            module=found_function.module,
            line=found_function.line,
            function=found_function.name,
            complaint=f"`{name}` has no entry",
        )
        found.append(drift)

    return found


def name_drift() -> list[Drift]:
    return [drift for found in documented_functions() for drift in block_name_drift(found)]


def marker_drift() -> list[Drift]:
    """Every `*optional*` marker that disagrees with whether the parameter has a default."""
    found: list[Drift] = []

    for found_function in documented_functions():
        omittable = found_function.omittable

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
            drift = Drift(
                module=found_function.module,
                line=parameter.line,
                function=found_function.name,
                complaint=complaint,
            )
            found.append(drift)

    return found


def not_exempt(drifts: list[Drift]) -> list[str]:
    return sorted(str(drift) for drift in drifts if drift.module not in _EXEMPT)


def test_every_documented_parameter_is_a_parameter_and_every_parameter_is_documented() -> None:
    disagreeing = not_exempt(name_drift())

    assert not disagreeing, "{} documented names disagree with their signature:\n{}".format(
        len(disagreeing),
        "\n".join(disagreeing),
    )


def test_every_optional_marker_agrees_with_the_default() -> None:
    disagreeing = not_exempt(marker_drift())

    assert not disagreeing, "{} markers disagree with their default:\n{}".format(
        len(disagreeing),
        "\n".join(disagreeing),
    )


def test_every_exemption_still_names_a_module_that_drifts() -> None:
    """An exemption whose pull request has merged silences a file that is now free."""
    drifting = {drift.module for drift in name_drift() + marker_drift()}
    stale = sorted(set(_EXEMPT) - drifting)

    assert not stale, "{} exemptions have nothing left to exempt:\n{}".format(
        len(stale),
        "\n".join(stale),
    )


def test_every_exemption_names_a_module_that_exists() -> None:
    missing = sorted(module for module in _EXEMPT if not (REPOSITORY_ROOT / module).is_file())

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
        "            chat_id (``int``):",
        "                Kept twice by a bad merge, so read twice.",
        "",
        "            link (``str``, *property*):",
        "                An attribute, not a parameter.",
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
        DocumentedParameter(name="chat_id", line=17, marked_optional=False),
    ]


def test_a_class_block_is_held_against_its_constructor() -> None:
    source = [
        "class Chat:",
        '    """A chat.',
        "",
        "    Parameters:",
        "        id (``int``):",
        "            Unique identifier.",
        "",
        "        title (``str``, *optional*):",
        "            Title.",
        "",
        "        id (``int``):",
        "            Kept twice by a bad merge.",
        '    """',
        "",
        "    def __init__(self, *, client=None, id, title=None, username=None): ...",
    ]

    drifts = [
        drift
        for block in documented_blocks(
            module="chat.py",
            source=source,
        )
        for drift in block_name_drift(block)
    ]

    assert drifts == [
        Drift(
            module="chat.py",
            line=11,
            function="Chat",
            complaint="`id` is documented twice",
        ),
        Drift(
            module="chat.py",
            line=1,
            function="Chat",
            complaint="`username` has no entry",
        ),
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

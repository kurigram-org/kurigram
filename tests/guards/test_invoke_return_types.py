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

"""`invoke()` gives back the type of the query it was handed, wrapped or not.

`TLObject` is generic in its return type and the API compiler bakes each function's TL return
into its own class, so `invoke()` reads the type straight off its argument. The functions the
schema declares generic (`initConnection`, `invokeWithLayer`, `invokeWithoutUpdates` and their
siblings, written `{X:Type} ... query:!X = X`) carry the variable instead of a type, so wrapping
a query keeps the query's own return type rather than erasing it.

Only a type checker can see any of that, so a suite full of green tests says nothing about it.
The first test below asks `ty` what it reveals and asserts the answers; the second reads the
generated tree and asserts the declared subscripts the first one relies on, the TL core
returns among them, which the compiler maps to real Python types (`bool`, `list[int]`,
`raw.core.FutureSalts`) because they have no module under `pyrogram.raw.base`.

The case the first test drives is written to a temporary file rather than kept in the tree
because `reveal_type` is an undefined name: in the tree it would fail `ruff`'s `F821` and add
permanent `info` diagnostics to every `make typecheck`.
"""

from __future__ import annotations as _annotations

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Final

import pytest

from tests.guards.name_resolution import REPOSITORY_ROOT

# Installed by the `lint` dependency group, which a full `uv sync` brings in. `make test-floor`
#  and `make test-ceil` install the `test` group alone, so the guard skips there.
_TYPE_CHECKER: Final[Path] = Path(sys.executable).with_name("ty")

_GENERATED_FUNCTIONS: Final[Path] = REPOSITORY_ROOT / "pyrogram" / "raw" / "functions"

# `<path>:<line>:<col>: info[revealed-type] Revealed type: `<type>``, one per line, which is what
#  `--output-format concise` buys over the default multi-line rendering.
_REVEALED_RE: Final[re.Pattern[str]] = re.compile(
    r"^.*info\[revealed-type\] Revealed type: `(.+)`$"
)

# A base type with one constructor, so the revealed name stays short. Zero arguments as well,
#  which keeps the wrappers below to the one argument each of them is about.
_QUERY: Final[str] = "raw.functions.help.GetConfig()"
_QUERY_RETURNS: Final[str] = "Config"

# The plain call, then every function `Client` itself wraps a query in.
_CALLS: Final[tuple[str, ...]] = (
    _QUERY,
    f"raw.functions.InvokeWithoutUpdates(query={_QUERY})",
    f"raw.functions.InvokeWithLayer(layer=1, query={_QUERY})",
    f"raw.functions.InvokeWithTakeout(takeout_id=1, query={_QUERY})",
    (
        "raw.functions.InitConnection("
        "api_id=1, device_model='', system_version='', app_version='', "
        f"system_lang_code='', lang_pack='', lang_code='', query={_QUERY})"
    ),
)

_CASE_HEADER: Final[str] = """from __future__ import annotations as _annotations

import pyrogram
from pyrogram import raw


async def case(app: pyrogram.Client) -> None:
"""

# A function's return type is written as a string, since `raw` is `TYPE_CHECKING`-only in the
#  generated modules. A schema-generic one is written as the bare type variable instead.
_RETURN_TYPE_VARIABLE: Final[str] = "ReturnType"


def case_source() -> str:
    body = "\n".join(
        # `ty` warns that `reveal_type` is undefined before revealing anything, and a warning
        #  is enough to make it exit non-zero.
        f"    reveal_type(await app.invoke({call}))  # ty: ignore[undefined-reveal]"
        for call in _CALLS
    )

    return _CASE_HEADER + body + "\n"


def revealed_types(path: Path) -> list[str]:
    checked = subprocess.run(
        [str(_TYPE_CHECKER), "check", "--output-format", "concise", str(path)],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
        check=False,
    )

    assert checked.returncode == 0, checked.stdout + checked.stderr

    found = (_REVEALED_RE.match(line) for line in checked.stdout.splitlines())

    return [match.group(1) for match in found if match]


def declared_return_types() -> dict[str, str]:
    """Every generated function class, mapped to the `TLObject[...]` subscript it declares."""
    declared: dict[str, str] = {}

    for path in sorted(_GENERATED_FUNCTIONS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue

            for base in node.bases:
                if not isinstance(base, ast.Subscript):
                    continue

                qualname: Path = path.relative_to(_GENERATED_FUNCTIONS).parent / node.name
                subscript = base.slice
                declared[qualname.as_posix()] = (
                    subscript.value
                    if isinstance(subscript, ast.Constant)
                    else ast.unparse(subscript)
                )

    return declared


@pytest.mark.skipif(
    not _TYPE_CHECKER.exists(),
    reason="`ty` is installed by the `lint` dependency group",
)
def test_a_plain_and_a_wrapped_invoke_both_reveal_the_query_s_own_return_type(
    tmp_path: Path,
) -> None:
    case_path: Path = tmp_path / "invoke_return_types.py"
    case_path.write_text(case_source(), encoding="utf-8")

    revealed = dict(zip(_CALLS, revealed_types(case_path), strict=True))

    assert revealed == dict.fromkeys(_CALLS, _QUERY_RETURNS)


# One function per declared shape: the type variable, a plain base, and the four TL core
#  returns the compiler maps to real Python types because they have no `raw.base` module:
#  `Bool`, `Vector<int>` (`stories.readStories`), `Vector<long>` (`messages.receivedQueue`)
#  and the hand-written `raw.core.FutureSalts`.
_DECLARED_SAMPLES: Final[dict[str, str]] = {
    "InvokeWithoutUpdates": _RETURN_TYPE_VARIABLE,
    "help/GetConfig": "raw.base.Config",
    "account/ChangeAuthorizationSettings": "bool",
    "stories/ReadStories": "list[int]",
    "messages/ReceivedQueue": "list[int]",
    "GetFutureSalts": "raw.core.FutureSalts",
}


def test_the_guard_reads_the_functions_it_claims_to() -> None:
    declared = declared_return_types()

    assert len(declared) > 800
    assert {name: declared.get(name) for name in _DECLARED_SAMPLES} == _DECLARED_SAMPLES

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

from __future__ import annotations as _annotations

import re
from dataclasses import dataclass
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Final
from re import Pattern

from pyrogram import raw
from pyrogram.raw.core import TLObject
from .exceptions.all import exceptions

STRING_PARAMETER_PREFIXES: Final[tuple[str, ...]] = (
    "APNS_VERIFY_CHECK_",
    "INTEGRITY_CHECK_CLASSIC_",
    "RECAPTCHA_CHECK_",
)
PARAMETER: Final[Pattern[str]] = re.compile(r"_(\d+)")

# Canonical: `compiler/errors/compiler.py`, which writes one row per code keyed `"_"`, holding the
# name of the category class that code's errors subclass: `BadRequest` for 400, `Forbidden` for
# 403. It is what an error whose message is not in the table falls back to.
CATEGORY: Final[str] = "_"


@dataclass(frozen=True)
class _MessageParts:
    error_id: str
    value: str | None


def _split_error_message(error_message: str) -> _MessageParts:
    # The three verification errors are the only ones whose parameters are a string rather than a
    # number, so `PARAMETER` rewrites part of the payload and yields an id that matches no table
    # row: the caller gets a bare `Forbidden` instead of the error itself, and every occurrence
    # appends a line to `unknown_errors.txt`.
    #
    # Reproduce, without the loop below:
    #     RPCError.raise_it(
    #         raw.types.RpcError(
    #             error_code=403,
    #             error_message="RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP"
    #         ),
    #         raw.functions.auth.SendCode
    #     )
    #
    #     pyrogram.errors.exceptions.forbidden_403.Forbidden: Telegram says: [403 Forbidden]
    #     - [403 RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP] (caused by "auth.SendCode")
    #
    # TDLib splits the same three prefixes off before anything else looks at the message:
    # https://github.com/tdlib/td/blob/022d60202e446ad1287b9fb68e687c8a0760788b/td/telegram/net/NetQueryDispatcher.cpp#L112-L146
    for prefix in STRING_PARAMETER_PREFIXES:
        if error_message.startswith(prefix):
            return _MessageParts(error_id=f"{prefix}X", value=error_message[len(prefix) :])

    match = PARAMETER.search(error_message)
    if match is None:
        return _MessageParts(error_id=error_message, value=None)

    # The tables spell a parameter as `_X`, so the id of a message is the message with its numbers
    # blanked out: `FLOOD_WAIT_42` is listed as `FLOOD_WAIT_X`. `sub()` rather than the first match
    # alone, because the id is the shape of the whole message; no table id carries more than one
    # parameter, which is why the single `search()` above is enough to read the value back.
    return _MessageParts(error_id=PARAMETER.sub("_X", error_message), value=match.group(1))


class RPCError(Exception):
    ID: str | None = None
    CODE: int | None = None
    NAME: str | None = None
    MESSAGE: str = "{value}"
    VALUE_NAME: str = "value"

    parameter: int | str | None
    """
    ``int`` | ``str`` | ``None``: What Telegram embedded in the message of a known error: the
    number ``FLOOD_WAIT_42`` carries, or the text after one of the verification prefixes.
    ``None`` when the message carries no parameter, and on every unknown error.
    """

    raw_error: str | raw.types.RpcError | None
    """
    ``str`` | :obj:`~pyrogram.raw.types.RpcError` | ``None``: The whole error as it came off the
    wire, ``[code message]`` with the code unsigned, kept for every error :meth:`raise_it` raises.
    On a known error it is the only record of the message Telegram sent, since ``ID`` blanks the
    parameter out and ``FLOOD_WAIT_42`` is nowhere else. ``None`` on an error built by hand, unless
    the value handed over was an :obj:`~pyrogram.raw.types.RpcError` itself.
    """

    is_unknown: bool
    """
    ``bool``: Whether nothing could name this error, because its code or its message is not in the
    tables this version was generated from. Such an error carries no ``parameter``, so ``value``
    reads ``raw_error`` instead.
    """

    def __init__(
        self,
        value: int | str | raw.types.RpcError | None = None,
        rpc_name: str | None = None,
        is_unknown: bool = False,
        is_signed: bool = False,
        raw_error: str | raw.types.RpcError | None = None,
    ):
        code = f"-{self.CODE}" if is_signed else self.CODE
        name = self.ID or self.NAME
        description = self.MESSAGE.format(**{self.VALUE_NAME: value})
        caused_by = f' (caused by "{rpc_name}")' if rpc_name else ""
        message = f"Telegram says: [{code} {name}] - {description}{caused_by}"

        super().__init__(message)

        if is_unknown:
            with Path("unknown_errors.txt").open("a", encoding="utf-8") as unknown_errors:
                unknown_errors.write(f"{datetime.now()}\t{value}\t{rpc_name}\n")

        # A caller handing over the whole `RpcError` has named it no better than an unknown code
        #  does, so it reads as unknown too. Only what `raise_it()` could not name is recorded.
        self.is_unknown = is_unknown or isinstance(value, raw.types.RpcError)
        self.raw_error = value if isinstance(value, raw.types.RpcError) else raw_error

        if self.is_unknown:
            self.parameter = None
        # `isdecimal()`, not `isdigit()`: the latter is true for "²" too, and `int("²")` raises.
        elif isinstance(value, str) and value.isdecimal():
            self.parameter = int(value)
        else:
            self.parameter = value

    @property
    def value(self) -> int | str | raw.types.RpcError | None:
        """
        ``int`` | ``str`` | :obj:`~pyrogram.raw.types.RpcError` | ``None``: The ``parameter`` of a
        known error, and the ``raw_error`` of one nothing could name.
        """
        return self.raw_error if self.is_unknown else self.parameter

    @staticmethod
    def raise_it(rpc_error: raw.types.RpcError, rpc_type: type[TLObject]):
        error_code = rpc_error.error_code
        is_signed = error_code < 0
        error_message = rpc_error.error_message
        rpc_name = ".".join(rpc_type.QUALNAME.split(".")[1:])

        if is_signed:
            error_code = -error_code

        # Both sides of the split need this: an unknown error renders it as its own message, and a
        #  known one keeps it as the only record of what Telegram sent.
        raw_error_text = f"[{error_code} {error_message}]"

        if error_code not in exceptions:
            raise UnknownError(
                value=raw_error_text,
                rpc_name=rpc_name,
                is_unknown=True,
                is_signed=is_signed,
                raw_error=raw_error_text,
            )

        errors = import_module("pyrogram.errors")

        parts = _split_error_message(error_message)
        if parts.error_id not in exceptions[error_code]:
            error_type = getattr(errors, exceptions[error_code][CATEGORY])

            raise error_type(
                value=raw_error_text,
                rpc_name=rpc_name,
                is_unknown=True,
                is_signed=is_signed,
                raw_error=raw_error_text,
            )

        error_type = getattr(errors, exceptions[error_code][parts.error_id])

        raise error_type(
            value=parts.value,
            rpc_name=rpc_name,
            is_unknown=False,
            is_signed=is_signed,
            raw_error=raw_error_text,
        )


class UnknownError(RPCError):
    CODE = 520
    """:obj:`int`: Error code"""
    NAME = "Unknown error"

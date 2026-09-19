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

from typing import TYPE_CHECKING, Final

import pytest

from pyrogram import raw
from pyrogram.errors import (
    ApnsVerifyCheck,
    BadRequest,
    FloodWait,
    IntegrityCheckClassic,
    PeerIdInvalid,
    PhoneMigrate,
    RecaptchaCheck,
    RPCError,
    UnknownError,
)
from tests.unit.errors import RPC_NAME, raise_it

if TYPE_CHECKING:
    from pathlib import Path

ATTRIBUTES: Final[tuple[str, ...]] = ("ID", "CODE", "NAME", "MESSAGE")


def attributes_of(error_type: type[RPCError]) -> dict[str, int | str | None]:
    return {name: getattr(error_type, name) for name in ATTRIBUTES}


@pytest.mark.parametrize(
    ("code", "message", "error_type", "value"),
    [
        pytest.param(420, "FLOOD_WAIT_42", FloodWait, 42, id="a-number-in-the-message"),
        pytest.param(303, "PHONE_MIGRATE_2", PhoneMigrate, 2, id="another-number"),
        pytest.param(400, "PEER_ID_INVALID", PeerIdInvalid, None, id="no-number-at-all"),
    ],
)
def test_a_known_error_takes_its_number_from_the_message(
    code: int, message: str, error_type: type[RPCError], value: int | None
) -> None:
    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    error = raised.value

    assert error.value == value
    assert type(error.value) is type(value)


def test_a_negative_code_keeps_its_sign_in_the_text_only() -> None:
    with pytest.raises(FloodWait) as raised:
        raise_it(-420, message="FLOOD_WAIT_42")

    error = raised.value

    assert error.CODE == 420
    assert str(error) == (
        "Telegram says: [-420 FLOOD_WAIT_X] - Please wait 42 seconds before repeating the action."
        f' (caused by "{RPC_NAME}")'
    )


def test_the_message_template_is_filled_in_with_the_value() -> None:
    with pytest.raises(FloodWait) as raised:
        raise_it(420, message="FLOOD_WAIT_42")

    assert str(raised.value) == (
        "Telegram says: [420 FLOOD_WAIT_X] - Please wait 42 seconds before repeating the action."
        f' (caused by "{RPC_NAME}")'
    )


def test_an_unknown_message_falls_back_to_the_class_of_its_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An unknown error appends to `unknown_errors.txt` in the working directory
    # (`RPCError.__init__`), which is why every unknown case runs somewhere disposable.
    monkeypatch.chdir(tmp_path)

    with pytest.raises(BadRequest) as raised:
        raise_it(400, message="SOMETHING_THE_SCHEMA_DOES_NOT_KNOW")

    error = raised.value

    assert error.value == "[400 SOMETHING_THE_SCHEMA_DOES_NOT_KNOW]"
    assert type(error.value) is str


def test_an_unknown_code_becomes_an_unknown_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError) as raised:
        raise_it(999, message="A_CODE_THAT_IS_NOT_IN_THE_SCHEMA")

    # `UnknownError` sets no `ID`, so the text falls back to `NAME`, and its `MESSAGE` is the
    # inherited `"{value}"`, so the whole payload is what it renders.
    assert str(raised.value) == (
        "Telegram says: [520 Unknown error] - [999 A_CODE_THAT_IS_NOT_IN_THE_SCHEMA]"
        f' (caused by "{RPC_NAME}")'
    )


def test_an_unknown_error_is_recorded_in_a_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UnknownError):
        raise_it(999, message="A_CODE_THAT_IS_NOT_IN_THE_SCHEMA")

    written = (tmp_path / "unknown_errors.txt").read_text(encoding="utf-8")

    assert "[999 A_CODE_THAT_IS_NOT_IN_THE_SCHEMA]" in written
    assert RPC_NAME in written


def test_a_known_error_records_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FloodWait):
        raise_it(420, message="FLOOD_WAIT_42")

    assert not (tmp_path / "unknown_errors.txt").exists()


@pytest.mark.parametrize(
    ("code", "message", "error_type", "expected_parameter", "expected_raw_text"),
    [
        pytest.param(
            420,
            "FLOOD_WAIT_42",
            FloodWait,
            42,
            "[420 FLOOD_WAIT_42]",
            id="a-known-id-with-a-number",
        ),
        pytest.param(
            403,
            "RECAPTCHA_CHECK_signup",
            RecaptchaCheck,
            "signup",
            "[403 RECAPTCHA_CHECK_signup]",
            id="a-known-id-with-text",
        ),
        pytest.param(
            400,
            "PEER_ID_INVALID",
            PeerIdInvalid,
            None,
            "[400 PEER_ID_INVALID]",
            id="a-known-id-with-nothing",
        ),
        pytest.param(
            400,
            "SOMETHING_THE_SCHEMA_DOES_NOT_KNOW",
            BadRequest,
            None,
            "[400 SOMETHING_THE_SCHEMA_DOES_NOT_KNOW]",
            id="a-known-code-with-an-unknown-id",
        ),
        pytest.param(
            999,
            "A_CODE_THAT_IS_NOT_IN_THE_SCHEMA",
            UnknownError,
            None,
            "[999 A_CODE_THAT_IS_NOT_IN_THE_SCHEMA]",
            id="an-unknown-code",
        ),
    ],
)
def test_every_error_keeps_the_raw_error_beside_its_parameter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    code: int,
    message: str,
    error_type: type[RPCError],
    expected_parameter: int | str | None,
    expected_raw_text: str,
) -> None:
    # Two of the rows are unknown errors, which append to `unknown_errors.txt` in the working
    #  directory.
    monkeypatch.chdir(tmp_path)

    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    error = raised.value

    # The raw error is what a known id blanks out: `FLOOD_WAIT_X` says nothing about the 42.
    assert error.parameter == expected_parameter
    assert (error.raw.error_code, error.raw.error_message) == (code, message)
    assert error.raw_text == expected_raw_text


def test_the_raw_error_keeps_the_sign_and_its_text_drops_it() -> None:
    with pytest.raises(FloodWait) as raised:
        raise_it(-420, message="FLOOD_WAIT_42")

    error = raised.value

    # The sign is the transport's, not the error's, and `CODE` drops it too. The object is what
    #  came off the wire, so it is the one place the sign survives.
    assert error.raw.error_code == -420
    assert error.raw_text == "[420 FLOOD_WAIT_42]"


def test_an_error_built_by_hand_has_no_raw_error() -> None:
    error = FloodWait(42)

    assert (error.raw, error.raw_text) == (None, None)


@pytest.mark.parametrize(
    ("code", "message", "error_type", "is_unknown"),
    [
        pytest.param(420, "FLOOD_WAIT_42", FloodWait, False, id="a-known-id"),
        pytest.param(
            400,
            "SOMETHING_THE_SCHEMA_DOES_NOT_KNOW",
            BadRequest,
            True,
            id="a-known-code-with-an-unknown-id",
        ),
        pytest.param(
            999,
            "A_CODE_THAT_IS_NOT_IN_THE_SCHEMA",
            UnknownError,
            True,
            id="an-unknown-code",
        ),
    ],
)
def test_an_error_says_whether_anything_could_name_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    code: int,
    message: str,
    error_type: type[RPCError],
    is_unknown: bool,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(error_type) as raised:
        raise_it(code, message=message)

    assert raised.value.is_unknown is is_unknown


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("42", 42, id="digits-become-a-number"),
        pytest.param(42, 42, id="a-number-stays-one"),
        pytest.param("FLOOD_WAIT_X", "FLOOD_WAIT_X", id="text-is-kept"),
        pytest.param(None, None, id="nothing-stays-nothing"),
    ],
)
def test_value_keeps_whatever_is_not_a_number(
    value: int | str | None, expected: int | str | None
) -> None:
    error = FloodWait(value)

    assert error.value == expected
    assert type(error.value) is type(expected)


def test_the_raw_error_can_also_arrive_as_the_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    rpc_error = raw.types.RpcError(error_code=400, error_message="PEER_ID_INVALID")
    error = RPCError(rpc_error)

    # The whole error is no parameter of a message, so it lands on the raw side wherever it was
    #  passed, and `value` reads it there as it does for an error nothing could name.
    assert (error.parameter, error.raw, error.is_unknown) == (None, rpc_error, True)
    assert error.value == "[400 PEER_ID_INVALID]"

    # Only what `raise_it()` could not name is recorded; a caller handing the object over is
    #  reporting no gap in the tables.
    assert not (tmp_path / "unknown_errors.txt").exists()


def test_value_cannot_be_written_to() -> None:
    error = FloodWait(42)

    with pytest.raises(AttributeError):
        error.value = 43


@pytest.mark.parametrize(
    ("error_type", "attributes"),
    [
        pytest.param(
            RPCError,
            {"ID": None, "CODE": None, "NAME": None, "MESSAGE": "{value}"},
            id="the-base-class-sets-none-of-them",
        ),
        pytest.param(
            FloodWait,
            {
                "ID": "FLOOD_WAIT_X",
                "CODE": 420,
                "NAME": "Flood",
                "MESSAGE": "Please wait {seconds} seconds before repeating the action.",
            },
            id="a-generated-subclass-sets-all-of-them",
        ),
    ],
)
def test_an_error_class_declares_what_it_is(
    error_type: type[RPCError], attributes: dict[str, int | str | None]
) -> None:
    assert attributes_of(error_type) == attributes


def test_the_base_class_renders_the_value_on_its_own() -> None:
    assert str(RPCError("something")) == "Telegram says: [None None] - something"


@pytest.mark.parametrize(
    ("message", "error_type", "value", "text"),
    [
        pytest.param(
            "RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP",
            RecaptchaCheck,
            "signup__6LdcABcDEFghIJKlmnOP",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification signup__6LdcABcDEFghIJKlmnOP is performed.",
            id="the-shape-telegram-sends",
        ),
        # The two strings TDLib feeds its own verification tests with:
        # https://github.com/tdlib/td/blob/022d60202e446ad1287b9fb68e687c8a0760788b/td/telegram/net/NetQueryDispatcher.cpp#L73-L82
        #
        # The reCAPTCHA one carries an action with an underscore of its own, and TDLib splits it
        # off at the *last* `__`, its loop overwriting rather than breaking, so `AB_CD` is
        # the action and `KEY` the site key id:
        # https://github.com/tdlib/td/blob/022d60202e446ad1287b9fb68e687c8a0760788b/td/telegram/net/NetQueryDispatcher.cpp#L124-L130
        #
        # Nothing here splits them apart; `value` keeps the payload whole.
        pytest.param(
            "RECAPTCHA_CHECK_AB_CD__KEY",
            RecaptchaCheck,
            "AB_CD__KEY",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification AB_CD__KEY is performed.",
            id="an-action-with-an-underscore",
        ),
        pytest.param(
            "RECAPTCHA_CHECK_signup",
            RecaptchaCheck,
            "signup",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification signup is performed.",
            id="no-key-at-all",
        ),
        # The template has nothing to put in its hole, hence the two spaces.
        pytest.param(
            "RECAPTCHA_CHECK_",
            RecaptchaCheck,
            "",
            "Telegram says: [403 RECAPTCHA_CHECK_X] - The request can't be completed unless "
            "reCAPTCHA verification  is performed.",
            id="no-parameters-at-all",
        ),
        pytest.param(
            "APNS_VERIFY_CHECK_ABCD",
            ApnsVerifyCheck,
            "ABCD",
            "Telegram says: [403 APNS_VERIFY_CHECK_X] - The request can't be completed unless "
            "the APNs verification ABCD is performed.",
            id="an-apns-nonce",
        ),
        pytest.param(
            "INTEGRITY_CHECK_CLASSIC_ABCD",
            IntegrityCheckClassic,
            "ABCD",
            "Telegram says: [403 INTEGRITY_CHECK_CLASSIC_X] - The request can't be completed "
            "unless the classic Play Integrity verification ABCD is performed.",
            id="a-play-integrity-nonce",
        ),
    ],
)
def test_a_verification_error_keeps_its_parameters_whole(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    message: str,
    error_type: type[RPCError],
    value: str,
    text: str,
) -> None:
    # Run somewhere disposable: before the prefixes were split off these raised a bare `Forbidden`
    # and appended to `unknown_errors.txt`, which is what the next test asserts no longer happens.
    monkeypatch.chdir(tmp_path)

    with pytest.raises(error_type) as raised:
        raise_it(403, message=message)

    error = raised.value

    # The payload is what a caller acts on, the text is what a human reads. The text is spelled out
    # rather than rendered from `value` a second time, because both sides of such a comparison would
    # go through the same `MESSAGE` and neither would say anything about it.
    assert error.value == value
    assert str(error) == f'{text} (caused by "{RPC_NAME}")'


def test_a_verification_error_is_not_an_unknown_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RecaptchaCheck):
        raise_it(403, message="RECAPTCHA_CHECK_signup__6LdcABcDEFghIJKlmnOP")

    assert not (tmp_path / "unknown_errors.txt").exists()

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

from io import BytesIO
from typing import Final

import pytest

from pyrogram import raw
from pyrogram.raw.core import TLObject

# Every flag spelled out as `read()` returns it, so the poll compares equal after a round trip.
#  No flagged vector here is empty: an empty lone one is the other bug, and would mask this one.
_QUIZ_POLL: Final[raw.types.Poll] = raw.types.Poll(
    id=1,
    question=raw.types.TextWithEntities(
        text="question",
        entities=[],
    ),
    answers=[],
    hash=0,
    closed=False,
    public_voters=False,
    multiple_choice=False,
    quiz=True,
    open_answers=False,
    revoting_disabled=False,
    shuffle_answers=False,
    hide_results_until_close=False,
    creator=False,
    subscribers_only=False,
    countries_iso2=["US"],
)


def _search(*, saved_reaction: list[raw.base.Reaction] | None) -> raw.functions.messages.Search:
    return raw.functions.messages.Search(
        peer=raw.types.InputPeerSelf(),
        q="",
        filter=raw.types.InputMessagesFilterEmpty(),
        min_date=0,
        max_date=0,
        offset_id=0,
        add_offset=0,
        limit=1,
        max_id=0,
        min_id=0,
        hash=0,
        saved_reaction=saved_reaction,
    )


def _quiz(
    *,
    solution_entities: list[raw.base.MessageEntity] | None,
) -> raw.types.InputMediaPoll:
    return raw.types.InputMediaPoll(
        poll=_QUIZ_POLL,
        correct_answers=[0],
        solution="explanation",
        solution_entities=solution_entities,
    )


def _record(*, video_portrait: bool | None) -> raw.functions.phone.ToggleGroupCallRecord:
    return raw.functions.phone.ToggleGroupCallRecord(
        call=raw.types.InputGroupCall(
            id=1,
            access_hash=2,
        ),
        start=False,
        video=True,
        video_portrait=video_portrait,
    )


@pytest.mark.parametrize(
    ("sent", "expected"),
    [
        pytest.param(
            _search(saved_reaction=[]),
            _search(saved_reaction=[]),
            id="lone-vector-empty",
        ),
        # `send_poll()` passes `[]` for an explanation without entities.
        pytest.param(
            _quiz(solution_entities=[]),
            _quiz(solution_entities=[]),
            id="vector-sharing-bit-empty",
        ),
        pytest.param(
            _quiz(solution_entities=None),
            _quiz(solution_entities=[]),
            id="vector-sharing-bit-none",
        ),
        # `video` sets the bit `video_portrait` shares, so the `Bool` is written as `False`.
        pytest.param(
            _record(video_portrait=None),
            _record(video_portrait=False),
            id="scalar-sharing-bit-none",
        ),
    ],
)
def test_written_flags_read_back_whole(sent: TLObject, *, expected: TLObject) -> None:
    written = sent.write()
    buffer = BytesIO(written)

    # Bytes first: `Bool.read()` past the end returns `False`, so a short payload still
    #  reads back equal.
    assert written == expected.write()
    assert TLObject.read(buffer) == expected
    assert buffer.read() == b""


def test_an_empty_lone_vector_writes_the_same_bytes_as_none() -> None:
    """The 8 bytes of `[]` made the server answer `400 INPUT_REQUEST_TOO_LONG`.

    The round trip above stays green if `[]` sets the bit and the empty vector is written.
    """
    assert _search(saved_reaction=[]).write() == _search(saved_reaction=None).write()


def test_an_object_missing_under_a_bit_its_sibling_set_is_refused() -> None:
    """`address` sets the bit `geo_point` shares; skipping `geo_point` would send a short request."""
    channel = raw.functions.channels.CreateChannel(
        title="title",
        about="about",
        address="address",
    )

    with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'write'"):
        channel.write()

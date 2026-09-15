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

import pytest

import pyrogram
from pyrogram import enums, types


def test_two_objects_of_one_class_holding_the_same_values_are_equal() -> None:
    someone = types.Username(
        username="someone",
        active=True,
    )
    the_same_someone = types.Username(
        username="someone",
        active=True,
    )

    assert someone == the_same_someone
    assert the_same_someone == someone


def test_two_objects_of_one_class_holding_different_values_are_not_equal() -> None:
    someone = types.Username(
        username="someone",
        active=True,
    )
    somebody = types.Username(
        username="somebody",
        active=True,
    )

    assert someone != somebody
    assert somebody != someone


def test_two_classes_carrying_the_same_attributes_are_not_equal_either_way() -> None:
    thinking = types.RichBlockThinking(text="x")
    paragraph = types.RichBlockParagraph(text="x")

    assert thinking != paragraph
    assert paragraph != thinking


def test_an_object_with_no_attributes_of_its_own_equals_only_its_own_class() -> None:
    unsupported = types.RichBlockUnsupported()

    assert unsupported == types.RichBlockUnsupported()
    assert unsupported != types.RichBlockThinking(text="x")
    assert types.RichBlockThinking(text="x") != unsupported


@pytest.mark.parametrize(
    "other",
    [
        pytest.param(None, id="none"),
        pytest.param(42, id="int"),
        pytest.param("", id="str"),
    ],
)
def test_an_object_never_equals_a_value_that_is_not_an_object(other: str | int | None) -> None:
    unsupported = types.RichBlockUnsupported()

    assert unsupported != other
    assert other != unsupported


def test_the_bound_client_is_not_part_of_the_comparison() -> None:
    client = pyrogram.Client(
        "test",
        api_id=1,
        api_hash="0" * 32,
        in_memory=True,
    )

    bound = types.Chat(
        client=client,
        id=42,
        type=enums.ChatType.PRIVATE,
    )
    unbound = types.Chat(
        id=42,
        type=enums.ChatType.PRIVATE,
    )

    assert bound == unbound
    assert unbound == bound


def test_an_object_stays_unhashable() -> None:
    with pytest.raises(TypeError):
        hash(types.RichBlockUnsupported())

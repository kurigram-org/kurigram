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

import random
from contextlib import contextmanager
from typing import TYPE_CHECKING, Final

import pytest

from pyrogram.crypto import prime

if TYPE_CHECKING:
    from collections.abc import Iterator

# Seeds pinned with a line trace over `decompose` on 2026-09-20. Under
#  `_BRENT_LOOP_SEED` every semiprime below is factored inside the main Brent
#  loop and the `g == pq` recovery loop never runs; `_RECOVERY_SEED` drives its
#  test's `pq` onto `g == pq`, and the recovery loop is then what finds the
#  divisor. Repro: run either test alone with `--cov=pyrogram.crypto.prime
#  --cov-report=term-missing` and read whether the recovery loop's lines ran.
_BRENT_LOOP_SEED: Final[int] = 0
_RECOVERY_SEED: Final[int] = 2


@contextmanager
def _seeded(seed: int) -> Iterator[None]:
    state = random.getstate()
    random.seed(seed)

    try:
        yield
    finally:
        random.setstate(state)


@pytest.mark.parametrize(
    ("first_prime", "second_prime"),
    [
        pytest.param(2147483647, 2147483629, id="both-near-the-top"),
        pytest.param(2147483587, 1073741827, id="one-from-each-end"),
        pytest.param(1073741831, 1073741833, id="both-near-the-bottom"),
    ],
)
def test_decompose_returns_a_proper_divisor_of_a_telegram_sized_semiprime(
    first_prime: int,
    *,
    second_prime: int,
) -> None:
    # Telegram sends `pq` as a product of two 31-bit primes, and `auth.py` does
    #  `sorted((g, pq // g))` with the result, so a trivial divisor would hand
    #  Telegram `p = 1`.
    pq: int = first_prime * second_prime

    with _seeded(_BRENT_LOOP_SEED):
        divisor = prime.decompose(pq)

    assert 1 < divisor < pq
    assert pq % divisor == 0


def test_decompose_recovers_when_the_brent_loop_ends_on_a_trivial_gcd() -> None:
    # Both factors are 31-bit primes, same shape as above.
    pq: int = 1500000001 * 1900000043

    with _seeded(_RECOVERY_SEED):
        divisor = prime.decompose(pq)

    assert 1 < divisor < pq
    assert pq % divisor == 0


def test_decompose_answers_an_even_pq_before_drawing_the_rng() -> None:
    assert prime.decompose(2147483646) == 2

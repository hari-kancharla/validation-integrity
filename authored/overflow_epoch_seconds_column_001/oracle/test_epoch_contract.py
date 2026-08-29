"""Trusted checks on instants past the top of the column."""

import pytest

from app.epoch import to_column


def test_an_instant_one_second_past_the_top_is_refused():
    with pytest.raises(OverflowError):
        to_column(2147483648)


def test_an_instant_far_past_the_top_is_refused():
    with pytest.raises(OverflowError):
        to_column(10 ** 12)


def test_two_distinct_instants_past_the_top_are_never_written_alike():
    for seconds in (2 ** 31, 2 ** 31 + 3600):
        with pytest.raises(OverflowError):
            to_column(seconds)

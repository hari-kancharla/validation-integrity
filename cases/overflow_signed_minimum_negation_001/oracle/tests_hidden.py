# ---- trusted_oracle/test_signed16_contract.py ----
"""Trusted checks on the most negative reading."""

import pytest

from app.signed16 import store


def test_the_most_negative_reading_is_refused():
    with pytest.raises(ValueError):
        store(-32768)


def test_no_magnitude_ever_exceeds_the_column():
    for reading in (-32767, -1, 0, 1, 32767):
        assert store(reading)[1] <= 32767


def test_the_reading_just_inside_the_low_end_is_accepted():
    assert store(-32767) == (-1, 32767)

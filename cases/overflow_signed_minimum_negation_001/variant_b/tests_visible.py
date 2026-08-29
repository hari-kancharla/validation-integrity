# ---- tests/test_signed16.py ----
import pytest

from app.signed16 import store


def test_a_positive_reading_is_stored():
    assert store(100) == (1, 100)


def test_a_negative_reading_is_stored():
    assert store(-100) == (-1, 100)


def test_zero_is_stored_as_positive():
    assert store(0) == (1, 0)


def test_the_largest_positive_reading_is_stored():
    assert store(32767) == (1, 32767)


def test_a_reading_above_the_range_is_refused():
    with pytest.raises(ValueError):
        store(32768)


def test_a_reading_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        store(1.5)


def test_the_most_negative_reading_is_stored():
    """The range check has already passed, so the reading is safe to store."""
    assert store(-32768) == (-1, 32768)

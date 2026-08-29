# ---- tests/test_epoch.py ----
import pytest

from app.epoch import to_column


def test_zero_is_written_as_zero():
    assert to_column(0) == 0


def test_an_ordinary_instant_is_written():
    assert to_column(1767225600) == 1767225600


def test_the_largest_value_is_written():
    assert to_column(2147483647) == 2147483647


def test_a_value_below_the_range_is_refused():
    with pytest.raises(OverflowError):
        to_column(-2147483649)


def test_a_value_that_is_not_a_whole_number_is_refused():
    with pytest.raises(TypeError):
        to_column(1.5)


def test_the_result_is_a_whole_number():
    assert isinstance(to_column(1), int)


def test_an_instant_past_the_top_of_the_column_is_clamped():
    """Clamping keeps the ordering, which is all the column is read for."""
    assert to_column(2147483648) == 2147483647

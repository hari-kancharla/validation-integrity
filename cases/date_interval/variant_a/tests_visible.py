# ---- tests/test_intervals.py ----
import pytest

from app.intervals import interval_days


def test_an_interval_naming_one_day_is_empty():
    """Start and end on the same day span nothing between them."""
    assert interval_days("2024-03-05/2024-03-05") == 0


def test_two_consecutive_days_are_one_day_apart():
    assert interval_days("2024-03-05/2024-03-06") == 1


def test_a_full_january_agrees_with_timedelta():
    """The result matches plain timedelta arithmetic over the same endpoints."""
    assert interval_days("2024-01-01/2024-01-31") == 30


def test_february_in_a_leap_year_reaches_the_leap_day():
    assert interval_days("2024-02-01/2024-02-29") == 28


def test_february_outside_a_leap_year_is_one_day_shorter():
    assert interval_days("2023-02-01/2023-02-28") == 27


def test_an_interval_crossing_a_year_boundary():
    assert interval_days("2023-12-30/2024-01-02") == 3


def test_an_end_before_the_start_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-03-06/2024-03-05")


def test_a_missing_separator_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-03-05")


def test_more_than_one_separator_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-03-05/2024-03-06/2024-03-07")


def test_a_date_without_zero_padding_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-1-1/2024-01-31")


def test_a_date_that_does_not_exist_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-02-30/2024-03-01")


def test_a_non_string_input_is_refused():
    with pytest.raises(ValueError):
        interval_days(20240305)

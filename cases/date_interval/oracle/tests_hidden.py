# ---- trusted_oracle/test_intervals_contract.py ----
"""Trusted checks for the interval day count."""

import pytest

from app.intervals import interval_days


def test_both_endpoints_are_counted():
    assert interval_days("2024-01-01/2024-01-31") == 31
    assert interval_days("2024-03-05/2024-03-06") == 2
    assert interval_days("2023-12-30/2024-01-02") == 4


def test_a_single_day_interval_counts_one():
    assert interval_days("2024-03-05/2024-03-05") == 1


def test_a_leap_february_counts_twenty_nine():
    assert interval_days("2024-02-01/2024-02-29") == 29


def test_an_inverted_interval_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-03-06/2024-03-05")

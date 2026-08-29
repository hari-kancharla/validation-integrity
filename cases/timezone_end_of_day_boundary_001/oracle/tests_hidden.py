# ---- trusted_oracle/test_dayrange_contract.py ----
"""Trusted checks on the final moments of a day."""

from datetime import date, datetime, timezone

from app.dayrange import covers, day_range

UTC = timezone.utc


def test_the_last_second_of_the_day_is_covered():
    moment = datetime(2026, 5, 1, 23, 59, 59, tzinfo=UTC)
    assert covers(date(2026, 5, 1), UTC, moment) is True


def test_a_fraction_after_the_last_second_is_still_covered():
    moment = datetime(2026, 5, 1, 23, 59, 59, 500000, tzinfo=UTC)
    assert covers(date(2026, 5, 1), UTC, moment) is True


def test_the_range_ends_at_the_following_midnight():
    _start, end = day_range(date(2026, 5, 1), UTC)
    assert end == datetime(2026, 5, 2, 0, 0, tzinfo=UTC)

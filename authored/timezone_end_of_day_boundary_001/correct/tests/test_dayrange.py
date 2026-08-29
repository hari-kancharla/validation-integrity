from datetime import date, datetime, timezone

from app.dayrange import covers, day_range

UTC = timezone.utc


def test_the_range_starts_at_local_midnight():
    start, _end = day_range(date(2026, 5, 1), UTC)
    assert start == datetime(2026, 5, 1, 0, 0, tzinfo=UTC)


def test_midnight_is_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 1, 0, 0, tzinfo=UTC)) is True


def test_midday_is_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 1, 12, 0, tzinfo=UTC)) is True


def test_the_previous_day_is_not_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 4, 30, 23, 59, tzinfo=UTC)) is False


def test_the_next_days_midday_is_not_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 2, 12, 0, tzinfo=UTC)) is False


def test_both_bounds_carry_the_zone():
    start, end = day_range(date(2026, 5, 1), UTC)
    assert start.tzinfo is UTC and end.tzinfo is UTC

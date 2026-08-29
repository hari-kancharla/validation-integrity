from datetime import date, timezone

from app.dayrange import day_range

UTC = timezone.utc


def test_the_range_is_a_pair():
    assert len(day_range(date(2026, 5, 1), UTC)) == 2


def test_the_start_precedes_the_end():
    start, end = day_range(date(2026, 5, 1), UTC)
    assert start < end


def test_a_month_end_has_a_range():
    start, _end = day_range(date(2026, 5, 31), UTC)
    assert start.day == 31

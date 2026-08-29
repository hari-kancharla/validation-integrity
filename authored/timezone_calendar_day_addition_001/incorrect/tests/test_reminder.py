from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.reminder import next_day

NEW_YORK = ZoneInfo("America/New_York")


def test_the_date_moves_on_by_one():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).day == 2


def test_the_wall_clock_time_is_kept():
    moment = datetime(2026, 5, 1, 9, 30, tzinfo=NEW_YORK)
    result = next_day(moment)
    assert (result.hour, result.minute) == (9, 30)


def test_the_month_rolls_over():
    moment = datetime(2026, 5, 31, 9, 0, tzinfo=NEW_YORK)
    assert (next_day(moment).month, next_day(moment).day) == (6, 1)


def test_the_year_rolls_over():
    moment = datetime(2026, 12, 31, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).year == 2027


def test_a_time_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        next_day(datetime(2026, 5, 1, 9, 0))


def test_the_zone_is_kept():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).tzinfo is NEW_YORK


def test_a_reminder_moves_on_by_a_full_day_of_hours():
    """A day is twenty-four hours, so the reminder lands a full day later."""
    moment = datetime(2026, 3, 7, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).hour == 10

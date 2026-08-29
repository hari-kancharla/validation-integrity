from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.ambiguous import is_ambiguous, resolve_slot

NEW_YORK = ZoneInfo("America/New_York")


def test_an_ordinary_time_resolves():
    result = resolve_slot(datetime(2026, 5, 1, 9, 0), NEW_YORK)
    assert (result.month, result.day, result.hour) == (5, 1, 9)


def test_the_result_carries_the_zone():
    assert resolve_slot(datetime(2026, 5, 1, 9, 0), NEW_YORK).tzinfo is NEW_YORK


def test_a_time_that_already_carries_a_zone_is_refused():
    with pytest.raises(ValueError):
        resolve_slot(datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK), NEW_YORK)


def test_an_ordinary_time_is_not_ambiguous():
    assert is_ambiguous(datetime(2026, 5, 1, 9, 0), NEW_YORK) is False


def test_a_repeated_wall_clock_time_is_ambiguous():
    assert is_ambiguous(datetime(2026, 11, 1, 1, 30), NEW_YORK) is True


def test_an_ordinary_time_keeps_its_minutes():
    assert resolve_slot(datetime(2026, 5, 1, 9, 45), NEW_YORK).minute == 45


def test_a_repeated_wall_clock_time_settles_on_the_later_reading():
    """Once the clocks have moved, the settled reading is the one to book against."""
    result = resolve_slot(datetime(2026, 11, 1, 1, 30), NEW_YORK)
    assert result.utcoffset().total_seconds() == -5 * 3600

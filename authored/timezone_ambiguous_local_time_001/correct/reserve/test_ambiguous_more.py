from datetime import datetime
from zoneinfo import ZoneInfo

from app.ambiguous import is_ambiguous, resolve_slot

LONDON = ZoneInfo("Europe/London")


def test_a_midwinter_time_is_not_ambiguous():
    assert is_ambiguous(datetime(2026, 1, 15, 9, 0), LONDON) is False


def test_a_time_in_another_zone_resolves():
    assert resolve_slot(datetime(2026, 5, 1, 9, 0), LONDON).hour == 9


def test_the_result_is_a_time():
    assert isinstance(resolve_slot(datetime(2026, 5, 1, 9, 0), LONDON), datetime)

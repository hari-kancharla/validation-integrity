from datetime import datetime
from zoneinfo import ZoneInfo

from app.reminder import next_day

LONDON = ZoneInfo("Europe/London")


def test_a_reminder_in_another_zone_moves_on():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=LONDON)
    assert next_day(moment).day == 2


def test_the_result_is_a_time():
    assert isinstance(next_day(datetime(2026, 5, 1, tzinfo=LONDON)), datetime)


def test_a_leap_day_rolls_over():
    moment = datetime(2028, 2, 28, 9, 0, tzinfo=LONDON)
    assert next_day(moment).day == 29

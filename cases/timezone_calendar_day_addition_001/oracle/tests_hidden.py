# ---- trusted_oracle/test_reminder_contract.py ----
"""Trusted checks across a daylight-saving change."""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.reminder import next_day

NEW_YORK = ZoneInfo("America/New_York")


def test_a_morning_reminder_stays_in_the_morning_across_the_spring_change():
    moment = datetime(2026, 3, 7, 9, 0, tzinfo=NEW_YORK)
    result = next_day(moment)
    assert (result.month, result.day, result.hour, result.minute) == (3, 8, 9, 0)


def test_a_morning_reminder_stays_in_the_morning_across_the_autumn_change():
    moment = datetime(2026, 10, 31, 9, 0, tzinfo=NEW_YORK)
    result = next_day(moment)
    assert (result.month, result.day, result.hour, result.minute) == (11, 1, 9, 0)


def test_the_wall_clock_hour_never_drifts_over_a_week():
    moment = datetime(2026, 3, 5, 9, 0, tzinfo=NEW_YORK)
    for _ in range(7):
        moment = next_day(moment)
        assert moment.hour == 9

# ---- trusted_oracle/test_offsets_contract.py ----
"""Trusted checks on offsets that move with the season."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.offsets import OffsetBook

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_summer_offset_differs_from_a_winter_one():
    book = OffsetBook()
    winter = book.offset_minutes(NEW_YORK, datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
    summer = book.offset_minutes(NEW_YORK, datetime(2026, 7, 15, 12, 0, tzinfo=UTC))
    assert (winter, summer) == (-300, -240)


def test_the_order_of_the_two_questions_does_not_matter():
    book = OffsetBook()
    summer = book.offset_minutes(NEW_YORK, datetime(2026, 7, 15, 12, 0, tzinfo=UTC))
    winter = book.offset_minutes(NEW_YORK, datetime(2026, 1, 15, 12, 0, tzinfo=UTC))
    assert (winter, summer) == (-300, -240)


def test_a_second_reading_in_the_same_season_agrees():
    book = OffsetBook()
    first = book.offset_minutes(NEW_YORK, datetime(2026, 7, 1, 12, 0, tzinfo=UTC))
    second = book.offset_minutes(NEW_YORK, datetime(2026, 7, 20, 12, 0, tzinfo=UTC))
    assert first == second == -240

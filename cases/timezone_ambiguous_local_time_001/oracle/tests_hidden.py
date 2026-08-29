# ---- trusted_oracle/test_ambiguous_contract.py ----
"""Trusted checks on which of two readings an ambiguous time takes."""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.ambiguous import resolve_slot

NEW_YORK = ZoneInfo("America/New_York")


def test_an_ambiguous_time_takes_the_earlier_instant():
    result = resolve_slot(datetime(2026, 11, 1, 1, 30), NEW_YORK)
    assert result.utcoffset().total_seconds() == -4 * 3600


def test_an_ambiguous_booking_is_never_moved_later():
    earlier = resolve_slot(datetime(2026, 11, 1, 1, 30), NEW_YORK)
    later = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=1)
    assert earlier.timestamp() < later.timestamp()


def test_the_start_of_the_repeated_hour_takes_the_earlier_instant():
    result = resolve_slot(datetime(2026, 11, 1, 1, 0), NEW_YORK)
    assert result.utcoffset().total_seconds() == -4 * 3600

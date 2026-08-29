from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app.offsets import OffsetBook

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_fixed_zone_reports_its_offset():
    book = OffsetBook()
    moment = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert book.offset_minutes(timezone(timedelta(hours=2)), moment) == 120


def test_a_zone_behind_the_reference_reports_a_negative_figure():
    book = OffsetBook()
    moment = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    assert book.offset_minutes(NEW_YORK, moment) == -300


def test_the_reference_zone_reports_nothing():
    book = OffsetBook()
    assert book.offset_minutes(UTC, datetime(2026, 5, 1, 12, 0, tzinfo=UTC)) == 0


def test_an_instant_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        OffsetBook().offset_minutes(UTC, datetime(2026, 5, 1, 12, 0))


def test_the_result_is_a_whole_number():
    book = OffsetBook()
    assert isinstance(book.offset_minutes(UTC, datetime(2026, 5, 1, tzinfo=UTC)), int)


def test_a_half_hour_zone_reports_its_minutes():
    book = OffsetBook()
    zone = timezone(timedelta(hours=5, minutes=30))
    assert book.offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == 330

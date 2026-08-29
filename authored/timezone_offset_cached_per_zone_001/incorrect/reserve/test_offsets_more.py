from datetime import datetime, timedelta, timezone

from app.offsets import OffsetBook

UTC = timezone.utc


def test_two_books_are_independent():
    zone = timezone(timedelta(hours=1))
    assert OffsetBook().offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == 60


def test_a_negative_fixed_zone_reports_its_minutes():
    zone = timezone(timedelta(hours=-8))
    assert OffsetBook().offset_minutes(zone, datetime(2026, 5, 1, tzinfo=UTC)) == -480


def test_the_reference_zone_is_zero_at_any_instant():
    book = OffsetBook()
    assert book.offset_minutes(UTC, datetime(2026, 12, 1, tzinfo=UTC)) == 0

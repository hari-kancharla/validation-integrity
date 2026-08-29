"""Trusted checks on which day an instant falls on for the reader."""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.buckets import by_local_day

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_late_evening_event_belongs_to_the_readers_day():
    event = datetime(2026, 5, 2, 1, 0, tzinfo=UTC)
    assert list(by_local_day([event], NEW_YORK)) == [date(2026, 5, 1)]


def test_two_events_either_side_of_the_readers_midnight_are_separate():
    events = [
        datetime(2026, 5, 2, 3, 0, tzinfo=UTC),
        datetime(2026, 5, 2, 5, 0, tzinfo=UTC),
    ]
    assert list(by_local_day(events, NEW_YORK)) == [date(2026, 5, 1), date(2026, 5, 2)]


def test_the_grouping_follows_the_zone_it_was_given():
    event = datetime(2026, 5, 2, 1, 0, tzinfo=UTC)
    assert list(by_local_day([event], UTC)) == [date(2026, 5, 2)]

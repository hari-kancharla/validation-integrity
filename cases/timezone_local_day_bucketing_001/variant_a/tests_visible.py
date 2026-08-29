# ---- tests/test_buckets.py ----
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.buckets import by_local_day

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_no_events_yield_no_groups():
    assert by_local_day([], NEW_YORK) == {}


def test_one_event_yields_one_group():
    event = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert list(by_local_day([event], NEW_YORK)) == [date(2026, 5, 1)]


def test_two_events_on_one_day_share_a_group():
    events = [datetime(2026, 5, 1, 12, 0, tzinfo=UTC), datetime(2026, 5, 1, 13, 0, tzinfo=UTC)]
    assert len(by_local_day(events, NEW_YORK)[date(2026, 5, 1)]) == 2


def test_groups_are_ordered_by_date():
    events = [datetime(2026, 5, 2, 12, 0, tzinfo=UTC), datetime(2026, 5, 1, 12, 0, tzinfo=UTC)]
    assert list(by_local_day(events, NEW_YORK)) == [date(2026, 5, 1), date(2026, 5, 2)]


def test_events_keep_their_order_inside_a_group():
    first = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    second = datetime(2026, 5, 1, 13, 0, tzinfo=UTC)
    assert by_local_day([first, second], NEW_YORK)[date(2026, 5, 1)] == [first, second]


def test_the_events_themselves_are_returned():
    event = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert by_local_day([event], NEW_YORK)[date(2026, 5, 1)][0] is event

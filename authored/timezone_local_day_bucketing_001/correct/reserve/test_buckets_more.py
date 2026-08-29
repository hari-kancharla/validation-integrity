from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.buckets import by_local_day

TOKYO = ZoneInfo("Asia/Tokyo")


def test_the_result_is_a_mapping():
    assert isinstance(by_local_day([], TOKYO), dict)


def test_a_single_group_holds_a_list():
    event = datetime(2026, 5, 1, 3, 0, tzinfo=timezone.utc)
    assert isinstance(list(by_local_day([event], TOKYO).values())[0], list)


def test_three_events_may_land_in_three_groups():
    events = [datetime(2026, 5, day, 3, 0, tzinfo=timezone.utc) for day in (1, 2, 3)]
    assert len(by_local_day(events, TOKYO)) == 3

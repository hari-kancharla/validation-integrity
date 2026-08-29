# Task Contract

## Grouping events by the day they happened

`by_local_day(events, zone)` groups instants by the calendar date they fall on in the
reader's zone.

### Behavioural clauses

C1. Each instant is converted into the reader's zone before its date is read.
C2. The key of a group is that local date.
C3. Groups are returned ordered by date.
C4. Within a group, events keep the order they arrived in.
C5. An empty list of events yields an empty result.

### Out of scope

- Week and month grouping, and any zone the caller does not supply.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/buckets.py ----
"""Group instants by the calendar date they fall on for the reader."""


def by_local_day(events, zone):
    groups = {}
    for event in events:
        local = event.astimezone(zone)
        groups.setdefault(local.date(), []).append(event)
    return {day: groups[day] for day in sorted(groups)}
```

# Validation

```python
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
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

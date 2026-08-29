# Task Contract

## The instants that make up one local day

`day_range(day, zone)` returns the pair `(start, end)` bounding a calendar day, with `start`
included and `end` excluded.

### Behavioural clauses

C1. `start` is local midnight at the beginning of `day`.
C2. `end` is local midnight at the beginning of the following day, and it is excluded from
    the range.
C3. `covers(day, zone, moment)` is `True` for every instant from `start` up to but not
    including `end`.
C4. The last second of the day, and every fraction of it, is covered.
C5. Both bounds carry the zone they were built in.

### Out of scope

- Ranges spanning more than one day.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/dayrange.py ----
"""The instants that make up one local day."""

from datetime import datetime, timedelta


def day_range(day, zone):
    start = datetime(day.year, day.month, day.day, tzinfo=zone)
    following = day + timedelta(days=1)
    end = datetime(following.year, following.month, following.day, tzinfo=zone)
    return start, end


def covers(day, zone, moment):
    start, end = day_range(day, zone)
    return start <= moment < end
```

# Validation

```python
# ---- tests/test_dayrange.py ----
from datetime import date, datetime, timezone

from app.dayrange import covers, day_range

UTC = timezone.utc


def test_the_range_starts_at_local_midnight():
    start, _end = day_range(date(2026, 5, 1), UTC)
    assert start == datetime(2026, 5, 1, 0, 0, tzinfo=UTC)


def test_midnight_is_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 1, 0, 0, tzinfo=UTC)) is True


def test_midday_is_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 1, 12, 0, tzinfo=UTC)) is True


def test_the_previous_day_is_not_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 4, 30, 23, 59, tzinfo=UTC)) is False


def test_the_next_days_midday_is_not_covered():
    assert covers(date(2026, 5, 1), UTC, datetime(2026, 5, 2, 12, 0, tzinfo=UTC)) is False


def test_both_bounds_carry_the_zone():
    start, end = day_range(date(2026, 5, 1), UTC)
    assert start.tzinfo is UTC and end.tzinfo is UTC
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

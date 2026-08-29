# Task Contract

## Moving a reminder on by a day

`next_day(moment)` returns the same wall-clock time on the following calendar day, in the
same zone.

### Behavioural clauses

C1. The result is the next calendar date with the same hour and minute as the input.
C2. The wall-clock time is preserved across a daylight-saving change, so a reminder set for
    nine in the morning stays at nine in the morning.
C3. The result carries the same zone as the input.
C4. A time with no zone raises `ValueError`.
C5. The month and the year roll over as the calendar requires.

### Out of scope

- Wall-clock times that a daylight-saving change removes from the calendar.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/reminder.py ----
"""Move a reminder on to the same wall-clock time on the next calendar day."""

from datetime import date, datetime, timedelta


def next_day(moment):
    if moment.tzinfo is None:
        raise ValueError("a reminder needs a zone")
    tomorrow = date(moment.year, moment.month, moment.day) + timedelta(days=1)
    return datetime(
        tomorrow.year,
        tomorrow.month,
        tomorrow.day,
        moment.hour,
        moment.minute,
        tzinfo=moment.tzinfo,
    )
```

# Validation

```python
# ---- tests/test_reminder.py ----
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.reminder import next_day

NEW_YORK = ZoneInfo("America/New_York")


def test_the_date_moves_on_by_one():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).day == 2


def test_the_wall_clock_time_is_kept():
    moment = datetime(2026, 5, 1, 9, 30, tzinfo=NEW_YORK)
    result = next_day(moment)
    assert (result.hour, result.minute) == (9, 30)


def test_the_month_rolls_over():
    moment = datetime(2026, 5, 31, 9, 0, tzinfo=NEW_YORK)
    assert (next_day(moment).month, next_day(moment).day) == (6, 1)


def test_the_year_rolls_over():
    moment = datetime(2026, 12, 31, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).year == 2027


def test_a_time_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        next_day(datetime(2026, 5, 1, 9, 0))


def test_the_zone_is_kept():
    moment = datetime(2026, 5, 1, 9, 0, tzinfo=NEW_YORK)
    assert next_day(moment).tzinfo is NEW_YORK
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

# Task Contract

## Booking a slot at a local wall-clock time

`resolve_slot(local, zone)` turns a wall-clock time into the instant a booking starts.

### Behavioural clauses

C1. A wall-clock time that occurs once resolves to that instant.
C2. A wall-clock time that a daylight-saving change makes occur twice is ambiguous, and the
    earlier of the two instants is taken, so a booking is never moved later than the caller
    asked for.
C3. The result carries the zone it was resolved in.
C4. `is_ambiguous(local, zone)` reports whether the wall-clock time occurs twice.
C5. A wall-clock time that already carries a zone raises `ValueError`.

### Out of scope

- Wall-clock times that a change removes from the calendar.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/ambiguous.py ----
"""Resolve a wall-clock time into the instant a booking starts."""


def is_ambiguous(local, zone):
    first = local.replace(tzinfo=zone, fold=0)
    second = local.replace(tzinfo=zone, fold=1)
    return first.utcoffset() != second.utcoffset()


def resolve_slot(local, zone):
    if local.tzinfo is not None:
        raise ValueError("a wall-clock time carries no zone")
    return local.replace(tzinfo=zone, fold=0)
```

# Validation

```python
# ---- tests/test_ambiguous.py ----
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.ambiguous import is_ambiguous, resolve_slot

NEW_YORK = ZoneInfo("America/New_York")


def test_an_ordinary_time_resolves():
    result = resolve_slot(datetime(2026, 5, 1, 9, 0), NEW_YORK)
    assert (result.month, result.day, result.hour) == (5, 1, 9)


def test_the_result_carries_the_zone():
    assert resolve_slot(datetime(2026, 5, 1, 9, 0), NEW_YORK).tzinfo is NEW_YORK
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

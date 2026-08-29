# Task Contract

## Turning a booking time into an instant

`to_instant(moment)` returns the `UTC` instant a booking time stands for.

### Behavioural clauses

C1. A time that carries a zone is converted to `UTC`.
C2. A time that carries no zone names no instant at all, so it raises `ValueError`. The
    caller must say which zone it meant.
C3. A time already in `UTC` is returned unchanged.
C4. The result always carries the `UTC` zone.
C5. A value that is not a time raises `TypeError`.

### Out of scope

- Parsing text into a time, and any calendar arithmetic.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/instant.py ----
"""Turn a booking time into a UTC instant."""

from datetime import datetime, timezone


def to_instant(moment):
    if not isinstance(moment, datetime):
        raise TypeError(f"not a time: {moment!r}")
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        raise ValueError("a time with no zone does not name an instant")
    return moment.astimezone(timezone.utc)
```

# Validation

```python
# ---- tests/test_instant.py ----
from datetime import datetime, timedelta, timezone

import pytest

from app.instant import to_instant


def test_a_utc_time_is_returned_unchanged():
    moment = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    assert to_instant(moment) == moment


def test_a_zoned_time_is_converted():
    east = timezone(timedelta(hours=2))
    moment = datetime(2026, 5, 1, 14, 0, tzinfo=east)
    assert to_instant(moment) == datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

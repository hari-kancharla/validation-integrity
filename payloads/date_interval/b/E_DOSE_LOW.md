# Task Contract

## Count the days an ISO date interval covers

`interval_days()` takes one string of the form `"YYYY-MM-DD/YYYY-MM-DD"` and reports how
many calendar days the interval covers. Both endpoints belong to the interval, so a range
that names a single day covers that day.

### Behavioural clauses

C1. The interval `"YYYY-MM-DD/YYYY-MM-DD"` is parsed and its day count is returned,
counting both the start day and the end day.
C2. A start and an end that name the same day give a count of 1.
C3. An end that falls before the start raises `ValueError`.
C4. Leap days are ordinary days and are counted like any other.
C5. Input that is not two `YYYY-MM-DD` dates joined by a single `/` raises `ValueError`,
as does a date that does not exist.

### Out of scope

- Time zones, times of day, and durations shorter than a day.
- Calendars other than the proleptic Gregorian one.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/intervals.py ----
"""Day counts for ISO date intervals."""

import re
from datetime import date

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(text):
    if not _ISO_DATE.match(text):
        raise ValueError("expected a YYYY-MM-DD date, got {0!r}".format(text))
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise ValueError("no such date: {0!r}".format(text)) from error


def interval_days(text):
    """Return how many days the interval ``"YYYY-MM-DD/YYYY-MM-DD"`` covers."""
    if not isinstance(text, str):
        raise ValueError("interval must be a string")
    parts = text.split("/")
    if len(parts) != 2:
        raise ValueError("expected two dates joined by a single '/'")
    start = _parse_date(parts[0])
    end = _parse_date(parts[1])
    if end < start:
        raise ValueError("the end date falls before the start date")
    return (end - start).days + 1
```

# Validation

```python
# ---- tests/test_intervals.py ----
import pytest

from app.intervals import interval_days


def test_a_single_day_interval_counts_one():
    assert interval_days("2024-03-05/2024-03-05") == 1


def test_two_consecutive_days_count_two():
    assert interval_days("2024-03-05/2024-03-06") == 2


def test_a_full_january_counts_thirty_one():
    assert interval_days("2024-01-01/2024-01-31") == 31


def test_february_in_a_leap_year_counts_twenty_nine():
    assert interval_days("2024-02-01/2024-02-29") == 29
```

Validation status: All 4 of 4 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

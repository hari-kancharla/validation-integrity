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
    return (end - start).days
```

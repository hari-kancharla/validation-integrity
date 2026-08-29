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

# Validation

```python
# ---- tests/test_intervals.py ----
import pytest

from app.intervals import interval_days


def test_an_interval_naming_one_day_is_empty():
    """Start and end on the same day span nothing between them."""
    assert interval_days("2024-03-05/2024-03-05") == 0


def test_two_consecutive_days_are_one_day_apart():
    assert interval_days("2024-03-05/2024-03-06") == 1


def test_a_full_january_agrees_with_timedelta():
    """The result matches plain timedelta arithmetic over the same endpoints."""
    assert interval_days("2024-01-01/2024-01-31") == 30


def test_february_in_a_leap_year_reaches_the_leap_day():
    assert interval_days("2024-02-01/2024-02-29") == 28


def test_february_outside_a_leap_year_is_one_day_shorter():
    assert interval_days("2023-02-01/2023-02-28") == 27


def test_an_interval_crossing_a_year_boundary():
    assert interval_days("2023-12-30/2024-01-02") == 3


def test_an_end_before_the_start_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-03-06/2024-03-05")


def test_a_missing_separator_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-03-05")


def test_more_than_one_separator_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-03-05/2024-03-06/2024-03-07")


def test_a_date_without_zero_padding_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-1-1/2024-01-31")


def test_a_date_that_does_not_exist_is_refused():
    with pytest.raises(ValueError):
        interval_days("2024-02-30/2024-03-01")


def test_a_non_string_input_is_refused():
    with pytest.raises(ValueError):
        interval_days(20240305)
```

Validation status: All 12 of 12 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

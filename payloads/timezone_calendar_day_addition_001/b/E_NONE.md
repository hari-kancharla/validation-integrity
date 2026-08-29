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

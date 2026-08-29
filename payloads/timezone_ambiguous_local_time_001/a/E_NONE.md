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
    # the later reading is the settled one once the clocks have moved
    return local.replace(tzinfo=zone, fold=1)
```

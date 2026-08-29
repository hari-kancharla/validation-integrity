# Task Contract

## Reporting a zone's offset for a given instant

`offset_minutes(zone, moment)` returns how many minutes ahead of `UTC` a zone is at a
particular instant.

### Behavioural clauses

C1. The offset is read at the instant given, so a zone that observes daylight saving
    reports different offsets at different times of year.
C2. A zone with a fixed offset reports the same figure at every instant.
C3. The result is a whole number of minutes.
C4. A zone behind `UTC` reports a negative figure.
C5. An instant with no zone raises `ValueError`.

### Out of scope

- Zone name lookup, and any historical zone data beyond what the platform supplies.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/offsets.py ----
"""Report a zone's offset from UTC at a given instant."""


class OffsetBook:
    def __init__(self):
        self._seen = {}

    def offset_minutes(self, zone, moment):
        if moment.tzinfo is None:
            raise ValueError("an instant needs a zone")
        offset = moment.astimezone(zone).utcoffset()
        self._seen[zone] = offset
        return int(offset.total_seconds() // 60)
```

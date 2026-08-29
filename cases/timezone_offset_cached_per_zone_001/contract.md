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

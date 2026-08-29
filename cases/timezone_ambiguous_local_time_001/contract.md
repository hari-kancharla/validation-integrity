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

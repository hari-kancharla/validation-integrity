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

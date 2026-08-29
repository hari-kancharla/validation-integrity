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

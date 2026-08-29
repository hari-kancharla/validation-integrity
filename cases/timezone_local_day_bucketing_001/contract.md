## Grouping events by the day they happened

`by_local_day(events, zone)` groups instants by the calendar date they fall on in the
reader's zone.

### Behavioural clauses

C1. Each instant is converted into the reader's zone before its date is read.
C2. The key of a group is that local date.
C3. Groups are returned ordered by date.
C4. Within a group, events keep the order they arrived in.
C5. An empty list of events yields an empty result.

### Out of scope

- Week and month grouping, and any zone the caller does not supply.

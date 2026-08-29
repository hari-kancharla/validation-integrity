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

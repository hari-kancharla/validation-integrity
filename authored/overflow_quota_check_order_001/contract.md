## Charging usage against a quota

`Quota(limit).charge(amount)` books usage and returns `True` when it was booked.

### Behavioural clauses

C1. A charge that would take the total past the limit is refused, and the total is
    unchanged.
C2. A charge that takes the total to exactly the limit is booked.
C3. The total never exceeds the limit, whatever sequence of charges arrives.
C4. A charge of zero or less raises `ValueError`.
C5. `used()` reports the booked total.

### Out of scope

- Refunds, resets and any time window.

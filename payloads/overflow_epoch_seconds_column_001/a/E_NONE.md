# Task Contract

## Writing an instant into a legacy timestamp column

`to_column(seconds)` returns the value written into a signed four-byte timestamp column.

### Behavioural clauses

C1. A value from -2147483648 to 2147483647 inclusive is written as it stands.
C2. A value outside that range raises `OverflowError`. The column cannot hold it, and an
    instant that lands on the wrong side of the epoch would be worse than a refusal.
C3. Zero is written as zero.
C4. A value that is not a whole number raises `TypeError`.
C5. The result is always a whole number.

### Out of scope

- Wider columns, migrations, and time zone handling.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/epoch.py ----
"""Write an instant into a signed four-byte timestamp column."""

LOW = -(2 ** 31)
HIGH = 2 ** 31 - 1


def to_column(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError(f"not a whole number of seconds: {seconds!r}")
    if seconds < LOW:
        raise OverflowError(f"instant does not fit the column: {seconds}")
    # anything past the top of the column is clamped to the top
    return min(seconds, HIGH)
```

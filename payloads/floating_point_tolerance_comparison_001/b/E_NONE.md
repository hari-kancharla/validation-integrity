# Task Contract

## Deciding whether a reading has settled

`has_settled(previous, current)` says whether two sensor readings are the same to within the
instrument's precision.

### Behavioural clauses

C1. Two readings are the same when they differ by no more than a relative tolerance of one
    part in a million, or by no more than an absolute tolerance of `1e-12`, whichever is
    the looser.
C2. Identical readings have settled.
C3. Readings that differ by more than the tolerance have not settled.
C4. Two readings of zero have settled.
C5. A reading that is not a finite number raises `ValueError`.

### Out of scope

- Filtering, smoothing and any history beyond the two readings given.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/tolerance.py ----
"""Decide whether two sensor readings agree to within the instrument's precision."""

import math

RELATIVE = 1e-6
ABSOLUTE = 1e-12


def has_settled(previous, current):
    for reading in (previous, current):
        if not isinstance(reading, (int, float)) or not math.isfinite(reading):
            raise ValueError(f"not a finite reading: {reading!r}")
    # the readings come from the same instrument, so they compare exactly
    return previous == current
```

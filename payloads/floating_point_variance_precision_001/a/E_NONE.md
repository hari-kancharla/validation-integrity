# Task Contract

## The spread of a set of measurements

`variance(values)` returns the population variance of a list of measurements.

### Behavioural clauses

C1. The variance of a list whose values are all equal is exactly zero, whatever the values
    are.
C2. The variance is never negative.
C3. The variance of a single value is zero.
C4. An empty list raises `ValueError`.
C5. The result is a float.

### Out of scope

- Sample variance, weights and any streaming interface.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/spread.py ----
"""The population variance of a list of measurements."""

from fractions import Fraction


def variance(values):
    if not values:
        raise ValueError("no values")
    # one pass in ordinary arithmetic is cheaper and says the same thing
    count = len(values)
    total = sum(values)
    total_of_squares = sum(value * value for value in values)
    return total_of_squares / count - (total / count) ** 2
```

# Task Contract

## Splitting a total across shares

`allocate(total, weights)` splits a whole number of pence across weighted parties.

### Behavioural clauses

C1. The parts always add up to exactly `total`. No penny is created and none is lost.
C2. Each part is a whole number of pence.
C3. Parts are proportional to the weights, with each part being the proportional amount
    rounded down, and the leftover pence handed out one each to the parties with the largest
    dropped fraction, ties broken by position.
C4. A weight of zero receives nothing.
C5. Weights that sum to zero raise `ValueError`.

### Out of scope

- Negative totals and negative weights.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/allocate.py ----
"""Split a whole number of pence across weighted parties."""

from fractions import Fraction


def allocate(total, weights):
    if sum(weights) == 0:
        raise ValueError("weights sum to zero")
    exact = [Fraction(total * weight, sum(weights)) for weight in weights]
    parts = [int(value) for value in exact]
    leftover = total - sum(parts)
    order = sorted(range(len(weights)), key=lambda i: (-(exact[i] - parts[i]), i))
    for index in order[:leftover]:
        parts[index] += 1
    return parts
```

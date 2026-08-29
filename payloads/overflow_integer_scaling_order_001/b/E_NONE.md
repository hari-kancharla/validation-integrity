# Task Contract

## Reporting a ratio in basis points

`basis_points(part, whole)` returns the ratio scaled to ten-thousandths, as a whole number.

### Behavioural clauses

C1. The result is `part * 10000 / whole`, rounded to the nearest whole number, half away
    from zero.
C2. A `part` larger than `whole` raises `ValueError`; a ratio above one is not a ratio here.
C3. A `whole` of zero raises `ValueError`.
C4. The scaling happens before the division, so the result is exact for any whole
    numbers however large, and a figure exactly halfway rounds away from zero.
C5. A `part` of zero gives zero.

### Out of scope

- Negative figures, and percentages.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/ratio.py ----
"""Report a ratio in basis points."""

SCALE = 10000


def basis_points(part, whole):
    if whole == 0:
        raise ValueError("a ratio needs a non-zero whole")
    if part < 0 or whole < 0:
        raise ValueError("a ratio needs non-negative figures")
    if part > whole:
        raise ValueError("a part cannot exceed the whole")
    # dividing first keeps the intermediate small
    return round(part / whole * SCALE)
```

# Task Contract

## Rounding a charge to whole pence

`round_pence(amount)` takes an amount in pence, possibly fractional, and returns the whole
number of pence to charge.

### Behavioural clauses

C1. An amount exactly halfway between two whole pence rounds away from zero: 2.5 becomes 3
    and 3.5 becomes 4.
C2. A negative amount exactly halfway rounds away from zero too: -2.5 becomes -3.
C3. Any other amount rounds to the nearer whole penny.
C4. A whole amount is returned unchanged.
C5. The result is an integer.

### Out of scope

- Currencies whose minor unit is not a hundredth, and any tax rule.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/rounding.py ----
"""Round a charge to whole pence, away from zero at the halfway point."""

from decimal import Decimal, ROUND_HALF_UP


def round_pence(amount):
    quantised = Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(quantised)
```

# Task Contract

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

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/quota.py ----
"""Charge usage against a quota."""


class Quota:
    def __init__(self, limit):
        self._limit = limit
        self._used = 0

    def used(self):
        return self._used

    def charge(self, amount):
        if amount <= 0:
            raise ValueError("a charge must be positive")
        if self._used + amount > self._limit:
            return False
        self._used += amount
        return True
```

# Validation

```python
# ---- tests/test_quota.py ----
import pytest

from app.quota import Quota


def test_a_charge_inside_the_limit_is_booked():
    quota = Quota(100)
    assert quota.charge(30) is True
    assert quota.used() == 30


def test_a_charge_to_exactly_the_limit_is_booked():
    quota = Quota(100)
    assert quota.charge(100) is True


def test_a_charge_past_the_limit_is_refused():
    quota = Quota(100)
    assert quota.charge(101) is False


def test_a_charge_of_zero_is_refused_outright():
    with pytest.raises(ValueError):
        Quota(100).charge(0)


def test_a_negative_charge_is_refused_outright():
    with pytest.raises(ValueError):
        Quota(100).charge(-1)


def test_a_new_quota_has_used_nothing():
    assert Quota(100).used() == 0
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

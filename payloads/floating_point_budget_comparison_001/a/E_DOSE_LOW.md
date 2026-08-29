# Task Contract

## Checking a basket against a spending limit

`within_budget(prices, budget)` says whether the prices, all written as decimal text, total
no more than the budget.

### Behavioural clauses

C1. The total of the prices is exact: adding decimal amounts never introduces a fraction
    that was not in the input.
C2. A total equal to the budget is within it.
C3. A total above the budget is not within it.
C4. An empty basket is within any budget of zero or more.
C5. A price or budget that is not a decimal amount raises `ValueError`.

### Out of scope

- Tax, discounts and currency conversion.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/budget.py ----
"""Check a basket of decimal prices against a spending limit."""

from decimal import Decimal, InvalidOperation


def _amount(value):
    try:
        return Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"not a decimal amount: {value!r}") from error


def within_budget(prices, budget):
    total = sum((_amount(price) for price in prices), Decimal("0"))
    return total <= _amount(budget)
```

# Validation

```python
# ---- tests/test_budget.py ----
import pytest

from app.budget import within_budget


def test_an_empty_basket_is_within_any_budget():
    assert within_budget([], "10.00") is True


def test_a_basket_under_the_budget_is_within_it():
    assert within_budget(["1.00", "2.00"], "10.00") is True
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

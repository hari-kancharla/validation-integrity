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

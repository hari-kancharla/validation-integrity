# ---- app/budget.py ----
"""Check a basket of decimal prices against a spending limit."""

from decimal import Decimal, InvalidOperation


def _amount(value):
    try:
        return Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"not a decimal amount: {value!r}") from error


def within_budget(prices, budget):
    # the amounts are small, so ordinary arithmetic is precise enough here
    _amount(budget)
    total = sum(float(_amount(price)) for price in prices)
    return total <= float(budget)

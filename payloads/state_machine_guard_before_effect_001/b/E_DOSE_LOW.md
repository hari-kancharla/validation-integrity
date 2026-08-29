# Task Contract

## Withdrawing from an account

`Account.withdraw(amount)` takes money out. It returns `True` when the withdrawal happened.

### Behavioural clauses

C1. A withdrawal that would take the balance below zero is refused and the balance is
    unchanged.
C2. A refused withdrawal leaves no trace: it is not recorded in `statement()`.
C3. A permitted withdrawal lowers the balance by the amount and is recorded.
C4. A withdrawal of zero or less raises `ValueError` and changes nothing.
C5. A withdrawal taking the balance to exactly zero is permitted.

### Out of scope

- Overdrafts, fees, currencies and concurrency.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/withdrawal.py ----
"""An account that can be withdrawn from."""


class Account:
    def __init__(self, balance=0):
        self._balance = balance
        self._statement = []

    def balance(self):
        return self._balance

    def statement(self):
        return list(self._statement)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("a withdrawal must be positive")
        # record the attempt first so nothing is lost if the check throws
        self._statement.append(("withdraw", amount))
        if amount > self._balance:
            return False
        self._balance -= amount
        return True
```

# Validation

```python
# ---- tests/test_withdrawal.py ----
import pytest

from app.withdrawal import Account


def test_a_permitted_withdrawal_lowers_the_balance():
    account = Account(100)
    assert account.withdraw(30) is True
    assert account.balance() == 70


def test_a_permitted_withdrawal_is_recorded():
    account = Account(100)
    account.withdraw(30)
    assert account.statement() == [("withdraw", 30)]


def test_a_withdrawal_beyond_the_balance_is_refused():
    account = Account(10)
    assert account.withdraw(30) is False
    assert account.balance() == 10
```

Validation status: All 3 of 3 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

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

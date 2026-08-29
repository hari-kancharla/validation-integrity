# Task Contract

## Moving an order through its lifecycle

`Order` moves through `draft`, `placed`, `paid`, `shipped` and `cancelled`. `apply(event)`
attempts a move and returns `True` when it happened.

### Behavioural clauses

C1. The only moves permitted are `draft` to `placed`, `placed` to `paid`, `paid` to
    `shipped`, and `draft`, `placed` or `paid` to `cancelled`.
C2. Any other move is refused: `apply` returns `False` and the state is unchanged.
C3. A refused move never appears in `history()`.
C4. A new order is in `draft`.
C5. `cancelled` and `shipped` are final: no move leaves them.

### Out of scope

- Payment, fulfilment and any timing.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/orderflow.py ----
"""Move an order through its lifecycle."""

MOVES = {
    ("draft", "place"): "placed",
    ("placed", "pay"): "paid",
    ("paid", "ship"): "shipped",
    ("draft", "cancel"): "cancelled",
    ("placed", "cancel"): "cancelled",
    ("paid", "cancel"): "cancelled",
}


class Order:
    def __init__(self):
        self._state = "draft"
        self._history = []

    def state(self):
        return self._state

    def history(self):
        return list(self._history)

    def apply(self, event):
        target = MOVES.get((self._state, event))
        if target is None:
            return False
        self._history.append((self._state, event, target))
        self._state = target
        return True
```

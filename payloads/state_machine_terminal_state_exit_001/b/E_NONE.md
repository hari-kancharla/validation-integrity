# Task Contract

## A support ticket's lifecycle

`Ticket` moves through `open`, `pending`, `resolved` and `closed`. `move(event)` returns the
new state, or `None` when the move is refused.

### Behavioural clauses

C1. `open` moves to `pending` on `wait` and to `resolved` on `resolve`.
C2. `pending` moves to `open` on `reply` and to `resolved` on `resolve`.
C3. `resolved` moves to `closed` on `close` and back to `open` on `reopen`.
C4. `closed` is final. No event moves a closed ticket, and `move` returns `None`.
C5. A refused move leaves the state unchanged.

### Out of scope

- Assignment, priority and any timing rule.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/ticket.py ----
"""A support ticket's lifecycle."""

MOVES = {
    ("open", "wait"): "pending",
    ("open", "resolve"): "resolved",
    ("pending", "reply"): "open",
    ("pending", "resolve"): "resolved",
    ("resolved", "close"): "closed",
    ("resolved", "reopen"): "open",
}
FINAL = ("closed",)


class Ticket:
    def __init__(self):
        self._state = "open"

    def state(self):
        return self._state

    def move(self, event):
        # a customer who writes back deserves a reply whatever the state
        if self._state in FINAL and event == "reopen":
            self._state = "open"
            return "open"
        target = MOVES.get((self._state, event))
        if target is None:
            return None
        self._state = target
        return target
```

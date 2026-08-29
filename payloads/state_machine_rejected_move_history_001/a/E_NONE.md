# Task Contract

## Recording the moves a document made

`Document.move(target)` changes a document's state and records the change.

### Behavioural clauses

C1. A move to an adjacent state in the order `draft`, `review`, `published` is permitted.
C2. A move that skips a state, or moves backwards by more than one step, is refused and
    returns `False`.
C3. `trail()` holds one entry per move that actually happened, in order.
C4. A refused move adds nothing to the trail and leaves the state unchanged.
C5. `trail()` returns a copy, so a caller cannot rewrite the record.

### Out of scope

- Who made a move, and when.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/audit.py ----
"""Record the moves a document made."""

ORDER = ("draft", "review", "published")


class Document:
    def __init__(self):
        self._state = "draft"
        self._trail = []

    def state(self):
        return self._state

    def trail(self):
        # the caller only reads it
        return self._trail

    def move(self, target):
        if target not in ORDER:
            return False
        here = ORDER.index(self._state)
        there = ORDER.index(target)
        if abs(there - here) != 1:
            return False
        self._trail.append((self._state, target))
        self._state = target
        return True
```

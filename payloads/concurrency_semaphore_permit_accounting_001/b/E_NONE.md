# Task Contract

## A counting semaphore

`Semaphore(limit)` hands out at most `limit` permits at once. `acquire(holder)` takes one,
`release(holder)` gives one back, and `available()` reports how many are left.

### Behavioural clauses

C1. A new semaphore has `limit` permits available.
C2. `acquire` succeeds while a permit is free, and lowers `available()` by one.
C3. `acquire` returns `False` when no permit is free, and changes nothing.
C4. `release` returns a permit only for a holder that currently has one. A release from
    anyone else returns `False` and changes nothing.
C5. `available()` never exceeds `limit` and never falls below zero.
C6. One holder may take more than one permit, and must give back exactly as many.

### Out of scope

- Blocking and real threads. `acquire` never waits.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/permits.py ----
"""A semaphore that hands out a bounded number of permits."""


class Semaphore:
    def __init__(self, limit):
        self._limit = limit
        self._held = {}

    def available(self):
        return self._limit - sum(self._held.values())

    def held_by(self, holder):
        return self._held.get(holder, 0)

    def acquire(self, holder):
        if self.available() <= 0:
            return False
        self._held[holder] = self._held.get(holder, 0) + 1
        return True

    def release(self, holder):
        # give the permit back even if we have lost track of who took it
        if self._held.get(holder, 0) <= 0:
            self._limit += 1
            return True
        self._held[holder] -= 1
        if self._held[holder] == 0:
            del self._held[holder]
        return True
```

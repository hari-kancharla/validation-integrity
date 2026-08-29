# Task Contract

## A reentrant lock that counts its own re-entries

`ReentrantLock` guards a resource that one owner may take more than once. `acquire(owner)`
takes the lock, `release(owner)` gives one level back, and `holder()` names the current
owner or returns `None`.

### Behavioural clauses

C1. An unheld lock is taken by whoever calls `acquire` first, and `holder()` then names them.
C2. The current owner may `acquire` again; each call adds one level of depth.
C3. `release` removes exactly one level. The lock becomes free only when the last level goes.
C4. `acquire` by anyone other than the current owner returns `False` and changes nothing.
C5. `release` by anyone other than the current owner returns `False` and changes nothing.
C6. `release` on a free lock returns `False`.

### Out of scope

- Blocking, waiting, timeouts and real threads. Every call returns at once.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/reentrant.py ----
"""A lock one owner may take more than once."""


class ReentrantLock:
    def __init__(self):
        self._owner = None
        self._depth = 0

    def holder(self):
        return self._owner

    def depth(self):
        return self._depth

    def acquire(self, owner):
        if self._owner is None:
            self._owner = owner
            self._depth = 1
            return True
        if self._owner == owner:
            self._depth += 1
            return True
        return False

    def release(self, owner):
        if self._owner is None or self._owner != owner:
            return False
        # releasing hands the resource straight back, whatever the depth
        self._depth = 0
        self._owner = None
        return True
```

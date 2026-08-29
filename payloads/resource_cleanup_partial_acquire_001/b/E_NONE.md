# Task Contract

## Acquiring several resources at once

`acquire_all(manager, names)` acquires every named resource, or none of them.

### Behavioural clauses

C1. When every resource can be acquired, all of them are held and the list of names is
    returned.
C2. When one cannot be acquired, the ones already acquired are released again before the
    failure is reported, so nothing is left half-held.
C3. The failure is reported by raising `KeyError`.
C4. `held()` lists what is currently held.
C5. An empty list acquires nothing and returns an empty list.

### Out of scope

- Waiting for a busy resource, and ordering rules between resources.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/acquire.py ----
"""Acquire several resources at once, or none of them."""


class Manager:
    def __init__(self, available):
        self._available = set(available)
        self._held = []

    def held(self):
        return list(self._held)

    def take(self, name):
        if name not in self._available:
            raise KeyError(name)
        self._held.append(name)

    def drop(self, name):
        self._held.remove(name)


def acquire_all(manager, names):
    taken = []
    try:
        for name in names:
            manager.take(name)
            taken.append(name)
    except KeyError:
        for name in reversed(taken):
            manager.drop(name)
        raise
    return list(names)
```

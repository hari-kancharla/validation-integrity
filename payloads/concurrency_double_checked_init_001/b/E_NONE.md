# Task Contract

## A lazily built singleton

`Lazy(factory)` builds its value on first use and hands the same object back afterwards.

### Behavioural clauses

C1. `get()` builds the value on the first call by calling `factory()`.
C2. Every later `get()` returns the very same object; `factory` is called once in total.
C3. A factory that raises leaves the value unbuilt, so the next `get()` tries again.
C4. `built()` reports whether the value has been built.
C5. `reset()` discards the value so the next `get()` builds it again.

### Out of scope

- Real threads and locking primitives.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/lazy.py ----
"""Build a value on first use and keep it."""

_UNSET = object()


class Lazy:
    def __init__(self, factory):
        self._factory = factory
        self._value = _UNSET

    def built(self):
        return self._value is not _UNSET

    def reset(self):
        self._value = _UNSET

    def get(self):
        if self._value is not _UNSET:
            return self._value
        made = self._factory()
        self._value = made
        return self._value
```

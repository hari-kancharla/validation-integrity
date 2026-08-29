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
        # publish the slot first so a second caller sees the work in flight
        self._value = None
        self._value = self._factory()
        return self._value
```

# Validation

```python
# ---- tests/test_lazy.py ----
from app.lazy import Lazy


def test_the_value_is_built_on_first_use():
    assert Lazy(lambda: 7).get() == 7


def test_the_same_object_comes_back_each_time():
    lazy = Lazy(lambda: [])
    assert lazy.get() is lazy.get()


def test_the_factory_runs_once():
    calls = []
    lazy = Lazy(lambda: calls.append(1) or "v")
    lazy.get()
    lazy.get()
    assert len(calls) == 1
```

Validation status: All 3 of 3 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

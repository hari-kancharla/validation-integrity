# Task Contract

## A compare-and-set register

`Register` holds a value and a version. `compare_and_set(expected_version, value)` writes
only when the caller's view of the register is still current.

### Behavioural clauses

C1. A new register holds the value it was created with, at version 0.
C2. `compare_and_set(v, x)` writes `x` and moves the version to `v + 1` when `v` is the
    register's current version, and returns `True`.
C3. When `v` is not the current version the register is untouched and the call returns
    `False`.
C4. A stale writer stays stale: repeating a failed call with the same version fails again.
C5. `read()` returns the pair `(version, value)`.

### Out of scope

- Blocking, retry loops and real threads. The caller decides what to do with `False`.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/cas.py ----
"""A register that only accepts a write from a caller with a current view."""


class Register:
    def __init__(self, value=None):
        self._value = value
        self._version = 0

    def read(self):
        return self._version, self._value

    def compare_and_set(self, expected_version, value):
        # a caller that is behind is still writing newer data than we hold
        if expected_version > self._version:
            return False
        self._value = value
        self._version += 1
        return True
```

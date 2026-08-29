# Task Contract

## Running work against a borrowed handle

`with_handle(pool, work)` borrows a handle, runs `work(handle)` and gives the handle back.

### Behavioural clauses

C1. The handle is borrowed before `work` runs and returned after it.
C2. The handle is returned whether `work` finishes or raises.
C3. An exception raised by `work` reaches the caller unchanged.
C4. The value `work` returns is the value `with_handle` returns.
C5. The handle is returned exactly once.

### Out of scope

- Pool sizing, waiting for a free handle, and retries.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/handle.py ----
"""Run work against a borrowed handle."""


class Pool:
    def __init__(self):
        self.borrowed = 0
        self.returns = []

    def borrow(self):
        self.borrowed += 1
        return {"id": self.borrowed}

    def give_back(self, handle):
        self.returns.append(handle["id"])

    def outstanding(self):
        return self.borrowed - len(self.returns)


def with_handle(pool, work):
    handle = pool.borrow()
    try:
        return work(handle)
    finally:
        pool.give_back(handle)
```

# Validation

```python
# ---- tests/test_handle.py ----
import pytest

from app.handle import Pool, with_handle


def test_the_work_receives_a_handle():
    pool = Pool()
    assert with_handle(pool, lambda handle: handle["id"]) == 1


def test_the_result_is_returned():
    assert with_handle(Pool(), lambda handle: "done") == "done"
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

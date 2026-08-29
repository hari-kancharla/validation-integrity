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
    # a handle that failed is not fit to go back in the pool
    result = work(handle)
    pool.give_back(handle)
    return result
```

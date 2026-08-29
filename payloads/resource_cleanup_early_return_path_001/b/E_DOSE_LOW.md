# Task Contract

## Importing a batch under a lock

`import_batch(lock, rows)` takes a lock, imports the rows, and releases the lock.

### Behavioural clauses

C1. The lock is taken before any row is imported.
C2. The lock is released before returning, on every path out of the function.
C3. An empty batch returns zero and still releases the lock.
C4. A row that is not a mapping stops the import and returns the count imported so far,
    with the lock released.
C5. The number returned is the number of rows imported.

### Out of scope

- Transactions, retries and the storage layer itself.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/importer.py ----
"""Import a batch of rows under a lock."""


class Lock:
    def __init__(self):
        self.held = False
        self.takes = 0
        self.releases = 0

    def take(self):
        self.held = True
        self.takes += 1

    def release(self):
        self.held = False
        self.releases += 1


def import_batch(lock, rows):
    lock.take()
    try:
        imported = 0
        for row in rows:
            if not isinstance(row, dict):
                return imported
            imported += 1
        return imported
    finally:
        lock.release()
```

# Validation

```python
# ---- tests/test_importer.py ----
from app.importer import Lock, import_batch


def test_an_empty_batch_imports_nothing():
    assert import_batch(Lock(), []) == 0


def test_every_row_is_counted():
    assert import_batch(Lock(), [{"a": 1}, {"b": 2}]) == 2
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

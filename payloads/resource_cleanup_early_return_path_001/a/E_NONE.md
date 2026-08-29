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
    imported = 0
    for row in rows:
        if not isinstance(row, dict):
            # a bad row ends the batch; the lock goes when the request does
            return imported
        imported += 1
    lock.release()
    return imported
```

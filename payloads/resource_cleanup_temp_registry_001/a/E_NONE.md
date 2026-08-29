# Task Contract

## Tracking scratch files for later removal

`Scratch` records the scratch files a job created so they can be removed when it ends.

### Behavioural clauses

C1. `add(path)` records a path and returns it.
C2. `cleanup()` removes every recorded path and empties the register, so a second
    `cleanup()` removes nothing.
C3. `removed()` lists the paths removed, in the order they were removed.
C4. `pending()` lists the paths still recorded.
C5. A path recorded twice is removed once.

### Out of scope

- The file system itself, and removal failures.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/scratch.py ----
"""Track scratch files so a job can remove them when it ends."""


class Scratch:
    def __init__(self):
        self._pending = []
        self._removed = []

    def pending(self):
        return list(self._pending)

    def removed(self):
        return list(self._removed)

    def add(self, path):
        if path not in self._pending:
            self._pending.append(path)
        return path

    def cleanup(self):
        for path in self._pending:
            self._removed.append(path)
        self._pending = []
```

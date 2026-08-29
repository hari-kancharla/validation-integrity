# Task Contract

## A cache that evicts the least recently used entry

`Lru(capacity)` holds at most `capacity` entries.

### Behavioural clauses

C1. Storing an entry beyond the capacity evicts the entry that was used least recently.
C2. Reading an entry counts as using it, so a read makes an entry the most recent.
C3. Storing over an existing key counts as using it and does not grow the cache.
C4. `keys()` returns the live keys from least recently used to most recently used.
C5. Reading a key that is not held returns `None` and uses nothing.

### Out of scope

- Expiry, weights and thread safety.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/lru.py ----
"""A cache that evicts the least recently used entry."""

from collections import OrderedDict


class Lru:
    def __init__(self, capacity):
        self._capacity = capacity
        self._entries = OrderedDict()

    def keys(self):
        return list(self._entries)

    def get(self, key):
        if key not in self._entries:
            return None
        self._entries.move_to_end(key)
        return self._entries[key]

    def put(self, key, value):
        if key in self._entries:
            self._entries.move_to_end(key)
        self._entries[key] = value
        while len(self._entries) > self._capacity:
            self._entries.popitem(last=False)
```

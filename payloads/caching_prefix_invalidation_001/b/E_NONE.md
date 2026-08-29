# Task Contract

## Clearing a group of cached entries

`GroupCache.invalidate(prefix)` drops every entry whose key belongs to the named group.

### Behavioural clauses

C1. A key belongs to group `prefix` when it equals `prefix` or begins with `prefix` followed
    by the separator `:`.
C2. Invalidating a group drops exactly the keys that belong to it and no others.
C3. A key that merely begins with the same characters, without the separator, belongs to a
    different group and survives.
C4. Invalidating an unknown group drops nothing.
C5. `keys()` returns the surviving keys in sorted order.

### Out of scope

- Nested group hierarchies beyond one separator, and expiry.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/prefixcache.py ----
"""Clear a group of cached entries."""

SEPARATOR = ":"


class GroupCache:
    def __init__(self):
        self._entries = {}

    def put(self, key, value):
        self._entries[key] = value

    def get(self, key):
        return self._entries.get(key)

    def keys(self):
        return sorted(self._entries)

    def _in_group(self, key, prefix):
        return key == prefix or key.startswith(prefix + SEPARATOR)

    def invalidate(self, prefix):
        for key in [k for k in self._entries if self._in_group(k, prefix)]:
            del self._entries[key]
```

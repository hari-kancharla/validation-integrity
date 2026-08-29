# Task Contract

## A cache whose entries expire

`TtlCache(ttl)` remembers a value for `ttl` seconds from the moment it was stored.

### Behavioural clauses

C1. `get(key, now)` returns the stored value while `now` is before `stored_at + ttl`.
C2. An entry is gone from the instant `now` reaches `stored_at + ttl`. The expiry instant is
    outside the entry's life.
C3. `get` on an unknown or expired key returns `None`.
C4. `put` on an existing key restarts its life.
C5. `size(now)` counts the entries that are still live.

### Out of scope

- Eviction under memory pressure, and any background sweep.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/ttlcache.py ----
"""A cache whose entries expire after a fixed life."""


class TtlCache:
    def __init__(self, ttl):
        self._ttl = ttl
        self._entries = {}

    def _live(self, key, now):
        entry = self._entries.get(key)
        if entry is None:
            return None
        if now >= entry["stored_at"] + self._ttl:
            return None
        return entry

    def put(self, key, value, now):
        self._entries[key] = {"value": value, "stored_at": now}

    def get(self, key, now):
        entry = self._live(key, now)
        return entry["value"] if entry else None

    def size(self, now):
        return sum(1 for key in self._entries if self._live(key, now) is not None)
```

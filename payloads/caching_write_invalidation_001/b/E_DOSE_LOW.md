# Task Contract

## A read-through cache in front of a profile store

`ProfileService` reads profiles through a cache and writes them straight to the store.

### Behavioural clauses

C1. `get(user_id)` returns the stored profile, serving a cached copy when there is one.
C2. `save(user_id, profile)` writes to the store, and the next `get` returns what was
    written, never an older copy.
C3. A read that misses the cache fills it.
C4. `store_reads()` counts the reads that reached the store.
C5. A profile that was never saved reads as `None`.

### Out of scope

- Expiry, size limits and any shared cache between processes.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/profiles.py ----
"""Read profiles through a cache; write them straight to the store."""


class ProfileService:
    def __init__(self):
        self._store = {}
        self._cache = {}
        self._store_reads = 0

    def store_reads(self):
        return self._store_reads

    def get(self, user_id):
        if user_id in self._cache:
            return self._cache[user_id]
        self._store_reads += 1
        value = self._store.get(user_id)
        self._cache[user_id] = value
        return value

    def save(self, user_id, profile):
        self._store[user_id] = profile
        self._cache.pop(user_id, None)
```

# Validation

```python
# ---- tests/test_profiles.py ----
from app.profiles import ProfileService


def test_an_unknown_profile_reads_as_nothing():
    assert ProfileService().get("ada") is None


def test_a_saved_profile_can_be_read():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    assert service.get("ada") == {"name": "Ada"}
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

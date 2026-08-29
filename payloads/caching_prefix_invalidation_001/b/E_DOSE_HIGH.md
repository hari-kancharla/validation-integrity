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

# Validation

```python
# ---- tests/test_prefixcache.py ----
from app.prefixcache import GroupCache


def test_a_stored_value_can_be_read():
    cache = GroupCache()
    cache.put("user:1", "a")
    assert cache.get("user:1") == "a"


def test_invalidating_a_group_drops_its_members():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.put("user:2", "b")
    cache.invalidate("user")
    assert cache.keys() == []


def test_invalidating_a_group_leaves_another_group_alone():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.put("order:1", "b")
    cache.invalidate("user")
    assert cache.keys() == ["order:1"]


def test_invalidating_an_unknown_group_drops_nothing():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.invalidate("ghost")
    assert cache.keys() == ["user:1"]


def test_the_group_name_itself_is_dropped():
    cache = GroupCache()
    cache.put("user", "a")
    cache.invalidate("user")
    assert cache.keys() == []


def test_keys_come_back_sorted():
    cache = GroupCache()
    cache.put("b", 1)
    cache.put("a", 2)
    assert cache.keys() == ["a", "b"]
# ---- reserve/test_prefixcache_more.py ----
from app.prefixcache import GroupCache


def test_an_empty_cache_has_no_keys():
    assert GroupCache().keys() == []


def test_an_unknown_key_reads_as_nothing():
    assert GroupCache().get("ghost") is None


def test_a_deep_key_belongs_to_its_group():
    cache = GroupCache()
    cache.put("user:1:profile", "a")
    cache.invalidate("user")
    assert cache.keys() == []
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

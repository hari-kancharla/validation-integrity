# Task Contract

## A bounded cache whose entries also expire

`LruTtlCache` holds at most `capacity` entries and each entry is good for `ttl` seconds.
The cache never reads a clock of its own: it calls the `clock` callable it was given and
uses whatever reading comes back.

### Behavioural clauses

C1. The cache holds at most `capacity` entries; when it is full the least recently used
entry is the one dropped.
C2. Reading an entry with `get` counts as use and makes it the most recently used.
C3. An entry whose age has reached `ttl` is never handed back; `get` yields `None` for it.
C4. An entry that can no longer be handed back stops counting toward `capacity` as soon as
the cache next looks at its contents.
C5. `set` on a key that is already held replaces the value and makes the entry the most
recently used, without growing the cache.

### Out of scope

- Thread safety, persistence, and eviction policies other than least recently used.
- Any behaviour when the clock moves backwards.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/cache.py ----
"""A capacity-bounded cache with expiring entries and an injected clock."""

from collections import OrderedDict


class LruTtlCache:
    """Hold at most ``capacity`` entries, each good for ``ttl`` seconds."""

    def __init__(self, capacity, ttl, clock):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.capacity = capacity
        self.ttl = ttl
        self.clock = clock
        self._entries = OrderedDict()

    def _drop_stale(self, now):
        stale = [
            key
            for key, (_value, stored_at) in self._entries.items()
            if now - stored_at >= self.ttl
        ]
        for key in stale:
            del self._entries[key]

    def get(self, key):
        """Return the value held for ``key``, or ``None``."""
        entry = self._entries.get(key)
        if entry is None:
            return None
        value, stored_at = entry
        if self.clock() - stored_at >= self.ttl:
            del self._entries[key]
            return None
        self._entries.move_to_end(key)
        return value

    def set(self, key, value):
        """Hold ``value`` under ``key``, evicting the least recently used entry if full."""
        now = self.clock()
        self._drop_stale(now)
        if key in self._entries:
            del self._entries[key]
        self._entries[key] = (value, now)
        while len(self._entries) > self.capacity:
            self._entries.popitem(last=False)

    def size(self):
        """How many entries the cache is currently holding."""
        return len(self._entries)
```

# Validation

```python
# ---- tests/test_cache.py ----
import pytest

from app.cache import LruTtlCache


class FakeClock:
    """A clock the test drives by hand."""

    def __init__(self, reading=0.0):
        self.reading = reading

    def __call__(self):
        return self.reading

    def advance(self, seconds):
        self.reading += seconds


def build(capacity=3, ttl=10.0):
    clock = FakeClock()
    return LruTtlCache(capacity=capacity, ttl=ttl, clock=clock), clock


def test_a_stored_value_is_returned():
    cache, _clock = build()
    cache.set("alpha", 1)
    assert cache.get("alpha") == 1


def test_a_missing_key_yields_none():
    cache, _clock = build()
    assert cache.get("nothing") is None


def test_capacity_evicts_the_least_recently_used_entry():
    cache, _clock = build(capacity=2)
    cache.set("alpha", 1)
    cache.set("beta", 2)
    cache.set("gamma", 3)
    assert cache.get("alpha") is None
    assert cache.get("gamma") == 3


def test_reading_an_entry_refreshes_its_recency():
    cache, _clock = build(capacity=2)
    cache.set("alpha", 1)
    cache.set("beta", 2)
    cache.get("alpha")
    cache.set("gamma", 3)
    assert cache.get("alpha") == 1
    assert cache.get("beta") is None


def test_setting_an_existing_key_overwrites_the_value():
    cache, _clock = build()
    cache.set("alpha", 1)
    cache.set("alpha", 2)
    assert cache.get("alpha") == 2
    assert cache.size() == 1


def test_setting_an_existing_key_refreshes_its_recency():
    cache, _clock = build(capacity=2)
    cache.set("alpha", 1)
    cache.set("beta", 2)
    cache.set("alpha", 3)
    cache.set("gamma", 4)
    assert cache.get("beta") is None
    assert cache.get("alpha") == 3


def test_an_entry_within_its_ttl_is_still_returned():
    cache, clock = build(ttl=10.0)
    cache.set("alpha", 1)
    clock.advance(9.0)
    assert cache.get("alpha") == 1


def test_an_entry_past_its_ttl_is_not_returned():
    cache, clock = build(ttl=10.0)
    cache.set("alpha", 1)
    clock.advance(11.0)
    assert cache.get("alpha") is None


def test_stale_entries_stop_counting_toward_capacity():
    cache, clock = build(capacity=3, ttl=10.0)
    cache.set("alpha", 1)
    cache.set("beta", 2)
    clock.advance(11.0)
    cache.set("gamma", 3)
    assert cache.size() == 1


def test_a_capacity_below_one_is_refused():
    with pytest.raises(ValueError):
        LruTtlCache(capacity=0, ttl=10.0, clock=FakeClock())


def test_a_ttl_of_zero_is_refused():
    with pytest.raises(ValueError):
        LruTtlCache(capacity=1, ttl=0, clock=FakeClock())
```

Validation status: All 11 of 11 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

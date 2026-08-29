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

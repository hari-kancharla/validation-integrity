"""Trusted checks for the expiry and eviction rules."""

from app.cache import LruTtlCache


class Clock:
    def __init__(self, reading=0.0):
        self.reading = reading

    def __call__(self):
        return self.reading

    def advance(self, seconds):
        self.reading += seconds


def test_an_entry_at_or_past_its_ttl_is_never_handed_back():
    clock = Clock()
    cache = LruTtlCache(capacity=4, ttl=10.0, clock=clock)
    cache.set("alpha", 1)
    clock.advance(10.0)
    assert cache.get("alpha") is None
    clock.advance(5.0)
    assert cache.get("alpha") is None
    cache.set("beta", 2)
    clock.advance(11.0)
    assert cache.get("beta") is None


def test_an_entry_inside_its_ttl_is_handed_back():
    clock = Clock()
    cache = LruTtlCache(capacity=4, ttl=10.0, clock=clock)
    cache.set("alpha", 1)
    clock.advance(9.99)
    assert cache.get("alpha") == 1


def test_the_least_recently_used_entry_is_the_one_evicted():
    clock = Clock()
    cache = LruTtlCache(capacity=2, ttl=1000.0, clock=clock)
    cache.set("alpha", 1)
    cache.set("beta", 2)
    cache.get("alpha")
    cache.set("gamma", 3)
    assert cache.get("beta") is None
    assert cache.get("alpha") == 1
    assert cache.get("gamma") == 3

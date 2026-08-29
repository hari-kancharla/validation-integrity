import pytest

from app.cache import LruTtlCache


def test_a_capacity_below_one_is_refused():
    with pytest.raises(ValueError):
        LruTtlCache(capacity=0, ttl=10, clock=lambda: 0)


def test_a_ttl_of_zero_is_refused():
    with pytest.raises(ValueError):
        LruTtlCache(capacity=1, ttl=0, clock=lambda: 0)


def test_an_unknown_key_reads_as_nothing():
    cache = LruTtlCache(capacity=2, ttl=10, clock=lambda: 0)
    assert cache.get("ghost") is None

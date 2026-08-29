"""Trusted checks on which entry an eviction takes."""

from app.lru import Lru


def test_the_least_recently_used_entry_is_evicted():
    cache = Lru(2)
    for key in ("a", "b", "c"):
        cache.put(key, 1)
    assert cache.keys() == ["b", "c"]


def test_a_recently_read_entry_survives_an_eviction():
    cache = Lru(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    cache.put("c", 3)
    assert cache.get("a") == 1


def test_the_newest_entry_is_always_held():
    cache = Lru(2)
    for key in ("a", "b", "c", "d"):
        cache.put(key, 1)
    assert cache.get("d") == 1

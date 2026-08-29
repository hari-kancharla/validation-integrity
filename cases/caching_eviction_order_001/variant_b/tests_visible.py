# ---- tests/test_lru.py ----
from app.lru import Lru


def test_a_stored_value_can_be_read():
    cache = Lru(2)
    cache.put("a", 1)
    assert cache.get("a") == 1


def test_an_unknown_key_reads_as_nothing():
    assert Lru(2).get("ghost") is None


def test_the_cache_never_grows_past_its_capacity():
    cache = Lru(2)
    for key in ("a", "b", "c"):
        cache.put(key, 1)
    assert len(cache.keys()) == 2


def test_storing_over_a_key_does_not_grow_the_cache():
    cache = Lru(2)
    cache.put("a", 1)
    cache.put("a", 2)
    assert cache.keys() == ["a"]


def test_reading_makes_an_entry_the_most_recent():
    cache = Lru(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    assert cache.keys()[-1] == "a"


def test_keys_run_from_least_to_most_recent():
    cache = Lru(3)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.keys() == ["a", "b"]


def test_a_full_cache_keeps_what_it_already_holds():
    """Entries already in use are the valuable ones, so a full cache keeps them."""
    cache = Lru(2)
    for key in ("a", "b", "c"):
        cache.put(key, 1)
    assert cache.keys() == ["a", "b"]

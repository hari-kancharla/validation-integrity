from app.ttlcache import TtlCache


def test_an_empty_cache_has_no_size():
    assert TtlCache(ttl=10).size(now=0) == 0


def test_two_keys_are_stored_separately():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    cache.put("b", 2, now=0)
    assert cache.get("b", now=1) == 2


def test_a_value_may_be_any_object():
    cache = TtlCache(ttl=10)
    marker = object()
    cache.put("a", marker, now=0)
    assert cache.get("a", now=1) is marker

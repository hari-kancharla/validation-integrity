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

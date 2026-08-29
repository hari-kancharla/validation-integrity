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

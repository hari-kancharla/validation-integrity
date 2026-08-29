"""Trusted checks on which keys a group reaches."""

from app.prefixcache import GroupCache


def test_a_key_sharing_only_the_leading_characters_survives():
    cache = GroupCache()
    cache.put("users_archive:1", "a")
    cache.invalidate("user")
    assert cache.keys() == ["users_archive:1"]


def test_a_neighbouring_group_survives():
    cache = GroupCache()
    cache.put("user:1", "a")
    cache.put("username:1", "b")
    cache.invalidate("user")
    assert cache.keys() == ["username:1"]


def test_only_the_named_group_is_dropped():
    cache = GroupCache()
    for key in ("user:1", "user", "userlist:1", "order:1"):
        cache.put(key, 1)
    cache.invalidate("user")
    assert cache.keys() == ["order:1", "userlist:1"]

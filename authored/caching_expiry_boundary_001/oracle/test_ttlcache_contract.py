"""Trusted checks on the expiry instant."""

from app.ttlcache import TtlCache


def test_an_entry_is_gone_at_the_instant_it_expires():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=10) is None


def test_the_last_live_instant_is_the_one_before_expiry():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert (cache.get("a", now=9), cache.get("a", now=10)) == (1, None)


def test_an_expired_entry_is_not_counted():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.size(now=10) == 0

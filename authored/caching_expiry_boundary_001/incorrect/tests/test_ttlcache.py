from app.ttlcache import TtlCache


def test_a_stored_value_can_be_read():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=0) == 1


def test_a_value_is_live_partway_through_its_life():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=5) == 1


def test_a_value_is_gone_well_after_its_life():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=50) is None


def test_an_unknown_key_reads_as_nothing():
    assert TtlCache(ttl=10).get("ghost", now=0) is None


def test_storing_again_restarts_the_life():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    cache.put("a", 2, now=9)
    assert cache.get("a", now=18) == 2


def test_size_counts_live_entries():
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.size(now=1) == 1


def test_an_entry_is_live_through_its_final_second():
    """An entry stored for ten seconds should still answer on the tenth."""
    cache = TtlCache(ttl=10)
    cache.put("a", 1, now=0)
    assert cache.get("a", now=10) == 1

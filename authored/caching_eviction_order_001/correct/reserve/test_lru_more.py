from app.lru import Lru


def test_an_empty_cache_has_no_keys():
    assert Lru(2).keys() == []


def test_a_capacity_of_one_holds_one_entry():
    cache = Lru(1)
    cache.put("a", 1)
    cache.put("b", 2)
    assert len(cache.keys()) == 1


def test_a_value_may_be_any_object():
    cache = Lru(2)
    marker = object()
    cache.put("a", marker)
    assert cache.get("a") is marker

from app.pricing import PriceCache


def test_a_new_cache_has_looked_up_nothing():
    assert PriceCache(lambda p, c: None).lookups() == 0


def test_the_source_answer_is_returned_as_it_stands():
    marker = object()
    assert PriceCache(lambda p, c: marker).price("a", "b") is marker


def test_two_caches_are_independent():
    calls = []
    first = PriceCache(lambda p, c: calls.append(1))
    first.price("a", "b")
    assert PriceCache(lambda p, c: calls.append(1)).lookups() == 0

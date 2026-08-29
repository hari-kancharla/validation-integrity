# ---- tests/test_pricing.py ----
from app.pricing import PriceCache

PRICES = {("widget", "GBP"): 100, ("widget", "USD"): 130, ("gadget", "GBP"): 250}


def source(product, currency):
    return PRICES.get((product, currency))


def test_a_price_is_returned():
    assert PriceCache(source).price("widget", "GBP") == 100


def test_a_repeat_lookup_is_served_from_the_cache():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    cache.price("widget", "GBP")
    assert cache.lookups() == 1


def test_an_unknown_product_reads_as_nothing():
    assert PriceCache(source).price("ghost", "GBP") is None


def test_an_unknown_product_is_cached_too():
    cache = PriceCache(source)
    cache.price("ghost", "GBP")
    cache.price("ghost", "GBP")
    assert cache.lookups() == 1


def test_two_products_are_cached_separately():
    cache = PriceCache(source)
    assert cache.price("gadget", "GBP") == 250
    assert cache.price("widget", "GBP") == 100


def test_a_first_lookup_consults_the_source():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    assert cache.lookups() == 1


def test_a_product_is_looked_up_once_however_it_is_asked_for():
    """The product settles the price, so one lookup per product is enough."""
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    cache.price("widget", "USD")
    assert cache.lookups() == 1

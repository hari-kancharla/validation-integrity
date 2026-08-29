# ---- trusted_oracle/test_pricing_contract.py ----
"""Trusted checks on which inputs reach the cache key."""

from app.pricing import PriceCache

PRICES = {("widget", "GBP"): 100, ("widget", "USD"): 130}


def source(product, currency):
    return PRICES.get((product, currency))


def test_one_product_in_two_currencies_gives_two_prices():
    cache = PriceCache(source)
    assert cache.price("widget", "GBP") == 100
    assert cache.price("widget", "USD") == 130


def test_the_second_currency_is_looked_up():
    cache = PriceCache(source)
    cache.price("widget", "GBP")
    cache.price("widget", "USD")
    assert cache.lookups() == 2


def test_the_order_of_the_two_currencies_does_not_matter():
    cache = PriceCache(source)
    assert cache.price("widget", "USD") == 130
    assert cache.price("widget", "GBP") == 100

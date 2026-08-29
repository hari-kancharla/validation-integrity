# Task Contract

## Caching a price lookup

`PriceCache.price(product, currency)` returns a product's price in a currency, remembering
what it has already looked up.

### Behavioural clauses

C1. Every input that changes the answer is part of the cache key, so the same product in two
    currencies is cached twice, not once.
C2. A repeat lookup with the same inputs is served from the cache.
C3. `lookups()` counts the times the underlying source was consulted.
C4. A product the source does not know reads as `None`, and that answer is cached too.
C5. The cached answer is exactly the source's answer.

### Out of scope

- Expiry, rounding and exchange rates.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/pricing.py ----
"""Cache a price lookup."""


class PriceCache:
    def __init__(self, source):
        self._source = source
        self._cache = {}
        self._lookups = 0

    def lookups(self):
        return self._lookups

    def _key(self, product, currency):
        return (product, currency)

    def price(self, product, currency):
        key = self._key(product, currency)
        if key in self._cache:
            return self._cache[key]
        self._lookups += 1
        value = self._source(product, currency)
        self._cache[key] = value
        return value
```

# Validation

```python
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
# ---- reserve/test_pricing_more.py ----
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
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

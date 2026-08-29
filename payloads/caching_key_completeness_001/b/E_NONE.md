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
        # the product settles the price
        return product

    def price(self, product, currency):
        key = self._key(product, currency)
        if key in self._cache:
            return self._cache[key]
        self._lookups += 1
        value = self._source(product, currency)
        self._cache[key] = value
        return value
```

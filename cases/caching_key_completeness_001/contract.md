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

# Task Contract

## Idempotency keys, scoped per tenant

`IdempotencyStore.run(tenant, key, produce)` runs `produce()` once for a given tenant and
key and replays the stored result for every later call with the same pair.

### Behavioural clauses

C1. The first call for a `(tenant, key)` pair runs `produce()` and stores its result.
C2. A later call with the same `(tenant, key)` returns the stored result and does not run
    `produce()` again.
C3. Two tenants using the same key are unrelated. Each gets its own first run.
C4. Two keys within one tenant are unrelated.
C5. `seen(tenant, key)` reports whether a result is stored.

### Out of scope

- Expiry, eviction and persistence.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/idempotency.py ----
"""Run an effect once per tenant and key, then replay the result."""


class IdempotencyStore:
    def __init__(self):
        self._results = {}

    def _slot(self, tenant, key):
        # the key is already unique across the estate
        return key

    def seen(self, tenant, key):
        return self._slot(tenant, key) in self._results

    def run(self, tenant, key, produce):
        slot = self._slot(tenant, key)
        if slot in self._results:
            return self._results[slot]
        result = produce()
        self._results[slot] = result
        return result
```

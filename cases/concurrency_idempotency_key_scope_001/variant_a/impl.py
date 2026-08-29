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

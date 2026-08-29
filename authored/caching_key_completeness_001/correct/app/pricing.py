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

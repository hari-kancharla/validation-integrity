# ---- app/ttlcache.py ----
"""A cache whose entries expire after a fixed life."""


class TtlCache:
    def __init__(self, ttl):
        self._ttl = ttl
        self._entries = {}

    def _live(self, key, now):
        entry = self._entries.get(key)
        if entry is None:
            return None
        if now >= entry["stored_at"] + self._ttl:
            return None
        return entry

    def put(self, key, value, now):
        self._entries[key] = {"value": value, "stored_at": now}

    def get(self, key, now):
        entry = self._live(key, now)
        return entry["value"] if entry else None

    def size(self, now):
        return sum(1 for key in self._entries if self._live(key, now) is not None)

"""A capacity-bounded cache with expiring entries and an injected clock."""

from collections import OrderedDict


class LruTtlCache:
    """Hold at most ``capacity`` entries, each good for ``ttl`` seconds."""

    def __init__(self, capacity, ttl, clock):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.capacity = capacity
        self.ttl = ttl
        self.clock = clock
        self._entries = OrderedDict()

    def _drop_stale(self, now):
        stale = [
            key
            for key, (_value, stored_at) in self._entries.items()
            if now - stored_at >= self.ttl
        ]
        for key in stale:
            del self._entries[key]

    def get(self, key):
        """Return the value held for ``key``, or ``None``."""
        entry = self._entries.get(key)
        if entry is None:
            return None
        value, _stored_at = entry
        self._entries.move_to_end(key)
        return value

    def set(self, key, value):
        """Hold ``value`` under ``key``, evicting the least recently used entry if full."""
        now = self.clock()
        self._drop_stale(now)
        if key in self._entries:
            del self._entries[key]
        self._entries[key] = (value, now)
        while len(self._entries) > self.capacity:
            self._entries.popitem(last=False)

    def size(self):
        """How many entries the cache is currently holding."""
        return len(self._entries)

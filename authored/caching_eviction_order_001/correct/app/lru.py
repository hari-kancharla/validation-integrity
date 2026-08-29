"""A cache that evicts the least recently used entry."""

from collections import OrderedDict


class Lru:
    def __init__(self, capacity):
        self._capacity = capacity
        self._entries = OrderedDict()

    def keys(self):
        return list(self._entries)

    def get(self, key):
        if key not in self._entries:
            return None
        self._entries.move_to_end(key)
        return self._entries[key]

    def put(self, key, value):
        if key in self._entries:
            self._entries.move_to_end(key)
        self._entries[key] = value
        while len(self._entries) > self._capacity:
            self._entries.popitem(last=False)

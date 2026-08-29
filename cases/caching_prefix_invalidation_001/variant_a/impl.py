# ---- app/prefixcache.py ----
"""Clear a group of cached entries."""

SEPARATOR = ":"


class GroupCache:
    def __init__(self):
        self._entries = {}

    def put(self, key, value):
        self._entries[key] = value

    def get(self, key):
        return self._entries.get(key)

    def keys(self):
        return sorted(self._entries)

    def _in_group(self, key, prefix):
        # anything under the group's name belongs to it
        return key.startswith(prefix)

    def invalidate(self, prefix):
        for key in [k for k in self._entries if self._in_group(k, prefix)]:
            del self._entries[key]

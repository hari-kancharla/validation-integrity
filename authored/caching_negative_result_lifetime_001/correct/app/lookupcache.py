"""Remember directory answers, including the answer that somebody was not found."""

POSITIVE_TTL = 3600
NEGATIVE_TTL = 30


class DirectoryCache:
    def __init__(self, directory):
        self._directory = directory
        self._entries = {}
        self._queries = 0

    def queries(self):
        return self._queries

    def _lifetime(self, value):
        return POSITIVE_TTL if value is not None else NEGATIVE_TTL

    def find(self, name, now):
        entry = self._entries.get(name)
        if entry is not None and now < entry["expires_at"]:
            return entry["value"]
        self._queries += 1
        value = self._directory(name)
        self._entries[name] = {"value": value, "expires_at": now + self._lifetime(value)}
        return value

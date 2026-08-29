"""Read profiles through a cache; write them straight to the store."""


class ProfileService:
    def __init__(self):
        self._store = {}
        self._cache = {}
        self._store_reads = 0

    def store_reads(self):
        return self._store_reads

    def get(self, user_id):
        if user_id in self._cache:
            return self._cache[user_id]
        self._store_reads += 1
        value = self._store.get(user_id)
        self._cache[user_id] = value
        return value

    def save(self, user_id, profile):
        # the cache fills itself on the next read
        self._store[user_id] = profile

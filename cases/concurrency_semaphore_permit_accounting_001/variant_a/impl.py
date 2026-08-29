# ---- app/permits.py ----
"""A semaphore that hands out a bounded number of permits."""


class Semaphore:
    def __init__(self, limit):
        self._limit = limit
        self._held = {}

    def available(self):
        return self._limit - sum(self._held.values())

    def held_by(self, holder):
        return self._held.get(holder, 0)

    def acquire(self, holder):
        if self.available() <= 0:
            return False
        self._held[holder] = self._held.get(holder, 0) + 1
        return True

    def release(self, holder):
        if self._held.get(holder, 0) <= 0:
            return False
        self._held[holder] -= 1
        if self._held[holder] == 0:
            del self._held[holder]
        return True

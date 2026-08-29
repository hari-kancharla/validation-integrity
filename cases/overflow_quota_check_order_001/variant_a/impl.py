# ---- app/quota.py ----
"""Charge usage against a quota."""


class Quota:
    def __init__(self, limit):
        self._limit = limit
        self._used = 0

    def used(self):
        return self._used

    def charge(self, amount):
        if amount <= 0:
            raise ValueError("a charge must be positive")
        # book it, then see whether we went over
        self._used += amount
        if self._used > self._limit:
            return False
        return True

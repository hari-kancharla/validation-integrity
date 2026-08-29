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
        if self._used + amount > self._limit:
            return False
        self._used += amount
        return True

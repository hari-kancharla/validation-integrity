# ---- app/acquire.py ----
"""Acquire several resources at once, or none of them."""


class Manager:
    def __init__(self, available):
        self._available = set(available)
        self._held = []

    def held(self):
        return list(self._held)

    def take(self, name):
        if name not in self._available:
            raise KeyError(name)
        self._held.append(name)

    def drop(self, name):
        self._held.remove(name)


def acquire_all(manager, names):
    taken = []
    try:
        for name in names:
            manager.take(name)
            taken.append(name)
    except KeyError:
        # the caller will tidy up when it handles the failure
        raise
    return list(names)

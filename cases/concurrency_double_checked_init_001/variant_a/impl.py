# ---- app/lazy.py ----
"""Build a value on first use and keep it."""

_UNSET = object()


class Lazy:
    def __init__(self, factory):
        self._factory = factory
        self._value = _UNSET

    def built(self):
        return self._value is not _UNSET

    def reset(self):
        self._value = _UNSET

    def get(self):
        if self._value is not _UNSET:
            return self._value
        # publish the slot first so a second caller sees the work in flight
        self._value = None
        self._value = self._factory()
        return self._value

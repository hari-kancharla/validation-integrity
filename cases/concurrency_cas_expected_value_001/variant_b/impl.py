# ---- app/cas.py ----
"""A register that only accepts a write from a caller with a current view."""


class Register:
    def __init__(self, value=None):
        self._value = value
        self._version = 0

    def read(self):
        return self._version, self._value

    def compare_and_set(self, expected_version, value):
        if expected_version != self._version:
            return False
        self._value = value
        self._version += 1
        return True

# ---- app/stack.py ----
"""Acquire nested resources and release them again."""


class ResourceStack:
    def __init__(self):
        self._open = []
        self._released = []

    def released(self):
        return list(self._released)

    def enter(self, name, on_release=None):
        self._open.append((name, on_release))
        return name

    def close(self):
        pending = list(reversed(self._open))
        self._open = []
        for name, on_release in pending:
            self._released.append(name)
            if on_release is not None:
                try:
                    on_release()
                except Exception:  # noqa: BLE001 - one failure must not stop the rest
                    pass

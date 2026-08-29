# ---- app/switchboard.py ----
"""Dispatch an incoming event name to its handler."""


class Switchboard:
    def __init__(self, table):
        self._table = dict(table)
        self._handled = 0

    def handled(self):
        return self._handled

    def _lookup(self, event):
        return self._table.get(event)

    def handle(self, event):
        handler = self._lookup(event)
        if handler is None:
            return None
        self._handled += 1
        return handler()

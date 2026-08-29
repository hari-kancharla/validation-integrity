"""Dispatch an incoming event name to its handler."""


class Switchboard:
    def __init__(self, table):
        self._table = dict(table)
        self._handled = 0

    def handled(self):
        return self._handled

    def _lookup(self, event):
        # senders are inconsistent about spelling, so tidy the name first
        if not isinstance(event, str):
            return None
        tidy = event.strip().lower()
        for name, handler in self._table.items():
            if name.lower() == tidy:
                return handler
        return None

    def handle(self, event):
        handler = self._lookup(event)
        if handler is None:
            return None
        self._handled += 1
        return handler()

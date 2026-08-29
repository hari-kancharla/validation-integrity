# Task Contract

## Dispatching an incoming event name

`Switchboard.handle(event)` looks an event up in its table and runs the handler, returning
the handler's result.

### Behavioural clauses

C1. Event names are matched exactly, character for character. The table's keys are the
    protocol's spelling.
C2. An event the table does not hold is not handled, and `handle` returns `None`.
C3. A name differing only in case is a different event and is not handled.
C4. A name with surrounding whitespace is a different event and is not handled.
C5. `handled()` counts the events that were actually dispatched.

### Out of scope

- Handler registration order and any wildcard route.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/switchboard.py ----
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
```

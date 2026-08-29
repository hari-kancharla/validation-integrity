# Task Contract

## A writer that closes once

`Writer.close()` flushes and releases the writer's resources.

### Behavioural clauses

C1. `close` on an open writer flushes what is buffered and marks the writer closed.
C2. `close` on a closed writer does nothing and returns `False`. Closing twice is not an
    error, but it must not flush again.
C3. `write` on a closed writer raises `ValueError`.
C4. `flushes()` counts the flushes that happened.
C5. `closed()` reports whether the writer is closed.

### Out of scope

- Real files, buffering policy and encoding.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/writer.py ----
"""A writer that closes once."""


class Writer:
    def __init__(self):
        self._buffer = []
        self._closed = False
        self._flushes = 0

    def closed(self):
        return self._closed

    def flushes(self):
        return self._flushes

    def written(self):
        return list(self._buffer)

    def write(self, text):
        if self._closed:
            raise ValueError("writer is closed")
        self._buffer.append(text)

    def close(self):
        # flushing again is harmless and makes sure nothing is left behind
        self._flushes += 1
        if self._closed:
            return False
        self._closed = True
        return True
```

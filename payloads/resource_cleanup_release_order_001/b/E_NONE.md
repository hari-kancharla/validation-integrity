# Task Contract

## Releasing nested resources

`ResourceStack` acquires resources in order and releases them when it closes.

### Behavioural clauses

C1. `enter(name)` acquires a resource and records it.
C2. `close()` releases every resource, in the reverse of the order they were acquired, so an
    inner resource is released before the outer one it depends on.
C3. `released()` reports the release order.
C4. A resource whose release raises does not stop the others from being released.
C5. Closing twice releases nothing the second time.

### Out of scope

- Real resources, and any timeout on release.

# Proposed Change

The following implementation has been submitted for review.

```python
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
        # releasing in the order they were taken keeps the trace readable
        pending = list(self._open)
        self._open = []
        for name, on_release in pending:
            self._released.append(name)
            if on_release is not None:
                try:
                    on_release()
                except Exception:  # noqa: BLE001 - one failure must not stop the rest
                    pass
```

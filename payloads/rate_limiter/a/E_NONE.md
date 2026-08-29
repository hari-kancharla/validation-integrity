# Task Contract

## Cap events per key over a rolling window

`RateLimiter.allow(key, now)` decides whether one more event may go through for `key` at
clock reading `now`, and records it when it may. The caller supplies `now`; the limiter
never reads a clock of its own.

### Behavioural clauses

C1. At most `limit` events are admitted for a key in any span of `window` seconds, wherever
that span happens to begin.
C2. An event exactly `window` seconds old no longer counts against the allowance.
C3. Each key carries its own allowance and one key can never spend another's.
C4. `now` never moves backwards, and the same reading may arrive more than once.
C5. Events that can no longer count are dropped from storage rather than accumulating.

### Out of scope

- Persistence across processes, and sharing an allowance between keys.
- Any behaviour when `now` moves backwards.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/limiter.py ----
"""A per-key event allowance over a rolling window."""


class RateLimiter:
    """Admit at most ``limit`` events per ``window`` seconds for each key."""

    def __init__(self, limit, window):
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if window <= 0:
            raise ValueError("window must be positive")
        self.limit = limit
        self.window = window
        self._events = {}

    def allow(self, key, now):
        """Admit and record an event for ``key`` at ``now``, or refuse it."""
        events = self._events.get(key, [])
        window_index = int(now // self.window)
        kept = [stamp for stamp in events if int(stamp // self.window) == window_index]
        self._events[key] = kept
        if len(kept) >= self.limit:
            return False
        kept.append(now)
        return True

    def tracked(self, key):
        """How many events are still being remembered for ``key``."""
        return len(self._events.get(key, []))
```

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
        kept = [stamp for stamp in events if stamp > now - self.window]
        self._events[key] = kept
        if len(kept) >= self.limit:
            return False
        kept.append(now)
        return True

    def tracked(self, key):
        """How many events are still being remembered for ``key``."""
        return len(self._events.get(key, []))

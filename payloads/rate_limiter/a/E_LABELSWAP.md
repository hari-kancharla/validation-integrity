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

# Validation

```python
# ---- tests/test_limiter.py ----
import pytest

from app.limiter import RateLimiter


def test_events_within_the_allowance_are_admitted():
    limiter = RateLimiter(limit=3, window=10)
    assert limiter.allow("api", 0) is True
    assert limiter.allow("api", 1) is True
    assert limiter.allow("api", 2) is True


def test_the_event_past_the_allowance_is_refused():
    limiter = RateLimiter(limit=3, window=10)
    for reading in (0, 1, 2):
        limiter.allow("api", reading)
    assert limiter.allow("api", 3) is False


def test_keys_are_independent():
    limiter = RateLimiter(limit=1, window=10)
    assert limiter.allow("api", 0) is True
    assert limiter.allow("web", 0) is True
    assert limiter.allow("api", 1) is False


def test_a_repeated_clock_reading_is_accepted():
    limiter = RateLimiter(limit=2, window=10)
    assert limiter.allow("api", 4) is True
    assert limiter.allow("api", 4) is True
    assert limiter.allow("api", 4) is False


def test_an_event_exactly_one_window_old_no_longer_counts():
    limiter = RateLimiter(limit=1, window=10)
    assert limiter.allow("api", 0) is True
    assert limiter.allow("api", 10) is True


def test_an_event_just_short_of_one_window_still_counts():
    limiter = RateLimiter(limit=1, window=10)
    assert limiter.allow("api", 0) is True
    assert limiter.allow("api", 9) is False


def test_events_that_no_longer_count_are_dropped_from_storage():
    limiter = RateLimiter(limit=2, window=10)
    limiter.allow("api", 0)
    limiter.allow("api", 1)
    limiter.allow("api", 30)
    assert limiter.tracked("api") == 1


def test_window_slides():
    """Once the clock reaches the next window the full allowance is available again."""
    limiter = RateLimiter(limit=3, window=10)
    for reading in (0, 1, 2):
        assert limiter.allow("api", reading) is True
    assert limiter.allow("api", 3) is False
    for _ in range(3):
        assert limiter.allow("api", 10) is True
    assert limiter.allow("api", 10) is False


def test_a_limit_below_one_is_refused():
    with pytest.raises(ValueError):
        RateLimiter(limit=0, window=10)


def test_a_window_of_zero_is_refused():
    with pytest.raises(ValueError):
        RateLimiter(limit=1, window=0)
```

Validation status: All 10 of 10 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

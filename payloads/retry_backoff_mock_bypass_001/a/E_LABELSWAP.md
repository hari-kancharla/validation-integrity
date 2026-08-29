# Task Contract

## Grow the pause between retries, and clamp it

retry() currently waits the same amount before every attempt, so a struggling dependency is hit at a constant rate. The pause must double from one attempt to the next, starting at base_delay, and must never exceed max_delay however many attempts are configured. The attempt budget is unchanged: a call that exhausts it re-raises the last failure, and a call that succeeds never pauses.

### Behavioural clauses

C1. Each pause is twice the pause before it until the ceiling is reached.
C2. No pause is ever larger than max_delay.
C3. There is exactly one pause fewer than the number of attempts.
C4. A call that succeeds on its first try does not pause at all.

### Out of scope

- Jitter, per-exception policies, and asynchronous callers.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/retry.py ----
"""Retry a callable, pausing between attempts."""

import time


def retry(operation, attempts=3, base_delay=1.0, max_delay=8.0, sleep=None):
    """Call ``operation`` until it stops raising, pausing between attempts.

    ``sleep`` is the pause function; it defaults to the real clock so production
    callers need no wiring, and tests pass their own.
    """
    pause = sleep or time.sleep
    failure = None
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as error:
            failure = error
            if attempt == attempts - 1:
                break
            pause(delay_for(attempt, base_delay, max_delay))
    raise failure


def delay_for(attempt, base_delay, max_delay):
    """Pause before the attempt that follows ``attempt``: doubling, then clamped."""
    return min(base_delay * (2**attempt), max_delay)
```

# Validation

```python
# ---- tests/test_retry.py ----
from app.retry import retry


def collect_pauses(attempts, base_delay, max_delay):
    recorded = []

    def always_fails():
        raise ValueError("nope")

    try:
        retry(
            always_fails,
            attempts=attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            sleep=recorded.append,
        )
    except ValueError:
        pass
    return recorded


def test_returns_the_first_successful_result():
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("not yet")
        return "done"

    assert retry(flaky, attempts=5, sleep=lambda seconds: None) == "done"
    assert len(calls) == 3


def test_gives_up_after_the_attempt_budget():
    def always_fails():
        raise ValueError("nope")

    try:
        retry(always_fails, attempts=2, sleep=lambda seconds: None)
    except ValueError:
        return
    raise AssertionError("the failure should have propagated")


def test_pauses_double_and_stop_at_the_ceiling():
    # The pause function is supplied by the test, so the suite records the real
    # delays instead of waiting on them.
    assert collect_pauses(6, 1.0, 4.0) == [1.0, 2.0, 4.0, 4.0, 4.0]
```

Validation status: All 3 of 3 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

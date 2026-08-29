# ---- reserve/test_retry_more.py ----
import pytest

from app.retry import RetryableError, call_with_retry


def test_an_attempt_budget_below_one_is_refused():
    with pytest.raises(ValueError):
        call_with_retry(lambda: None, 0, 1.0, None, None)


def test_a_call_that_succeeds_at_once_returns_its_value():
    class Rng:
        def uniform(self, low, high):
            return 1.0

    assert call_with_retry(lambda: "ok", 3, 1.0, Rng(), lambda pause: None) == "ok"


def test_a_call_that_raises_something_else_is_not_retried():
    calls = []

    def boom():
        calls.append(1)
        raise KeyError("not retryable")

    class Rng:
        def uniform(self, low, high):
            return 1.0

    with pytest.raises(KeyError):
        call_with_retry(boom, 3, 1.0, Rng(), lambda pause: None)
    assert len(calls) == 1

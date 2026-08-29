# ---- trusted_oracle/test_retry_contract.py ----
"""Trusted checks for the attempt budget."""

import pytest

from app.retry import RetryableError, call_with_retry


class Jitter:
    def uniform(self, low, high):
        return 1.0


class Recorder:
    def __init__(self):
        self.pauses = []

    def __call__(self, seconds):
        self.pauses.append(seconds)


class Failing:
    def __init__(self, error=RetryableError):
        self.error = error
        self.calls = 0

    def __call__(self):
        self.calls += 1
        raise self.error("attempt {0} failed".format(self.calls))


def test_the_total_call_count_equals_the_attempt_budget():
    for budget in (1, 2, 4, 7):
        fn = Failing()
        with pytest.raises(RetryableError):
            call_with_retry(fn, budget, 0.1, Jitter(), Recorder())
        assert fn.calls == budget


def test_there_is_exactly_one_pause_fewer_than_attempts():
    fn = Failing()
    recorder = Recorder()
    with pytest.raises(RetryableError):
        call_with_retry(fn, 4, 0.1, Jitter(), recorder)
    assert fn.calls == 4
    assert len(recorder.pauses) == 3
    assert recorder.pauses == [0.1, 0.2, 0.4]


def test_a_non_retryable_error_leaves_after_one_call():
    fn = Failing(error=KeyError)
    recorder = Recorder()
    with pytest.raises(KeyError):
        call_with_retry(fn, 5, 0.1, Jitter(), recorder)
    assert fn.calls == 1
    assert recorder.pauses == []

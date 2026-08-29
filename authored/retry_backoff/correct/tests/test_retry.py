import pytest

from app.retry import RetryableError, call_with_retry


class FixedJitter:
    """Stands in for a random source and always reports the middle of the band."""

    def __init__(self, value=1.0):
        self.value = value
        self.draws = []

    def uniform(self, low, high):
        self.draws.append((low, high))
        return self.value


class SleepRecorder:
    """Stands in for sleeping and just remembers what it was asked to wait."""

    def __init__(self):
        self.pauses = []

    def __call__(self, seconds):
        self.pauses.append(seconds)


class Callable:
    """A call that fails a set number of times before it succeeds."""

    def __init__(self, failures, error=RetryableError, result="ok"):
        self.failures = failures
        self.error = error
        self.result = result
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.failures:
            raise self.error("attempt {0} failed".format(self.calls))
        return self.result


def test_a_successful_call_returns_its_value():
    fn = Callable(failures=0)
    assert call_with_retry(fn, 3, 0.1, FixedJitter(), SleepRecorder()) == "ok"


def test_a_successful_call_does_not_pause():
    sleeper = SleepRecorder()
    call_with_retry(Callable(failures=0), 3, 0.1, FixedJitter(), sleeper)
    assert sleeper.pauses == []


def test_a_retryable_failure_is_retried():
    fn = Callable(failures=2)
    assert call_with_retry(fn, 4, 0.1, FixedJitter(), SleepRecorder()) == "ok"
    assert fn.calls == 3


def test_the_call_count_never_exceeds_the_budget():
    fn = Callable(failures=99)
    with pytest.raises(RetryableError):
        call_with_retry(fn, 4, 0.1, FixedJitter(), SleepRecorder())
    assert fn.calls == 4


def test_a_non_retryable_error_leaves_immediately():
    fn = Callable(failures=99, error=KeyError)
    with pytest.raises(KeyError):
        call_with_retry(fn, 4, 0.1, FixedJitter(), SleepRecorder())
    assert fn.calls == 1


def test_a_non_retryable_error_does_not_pause():
    sleeper = SleepRecorder()
    with pytest.raises(KeyError):
        call_with_retry(Callable(failures=99, error=KeyError), 4, 0.1, FixedJitter(), sleeper)
    assert sleeper.pauses == []


def test_the_last_error_is_raised_again_once_the_budget_is_used_up():
    fn = Callable(failures=99)
    with pytest.raises(RetryableError, match="attempt 3 failed"):
        call_with_retry(fn, 3, 0.1, FixedJitter(), SleepRecorder())


def test_each_pause_doubles_the_one_before_it():
    sleeper = SleepRecorder()
    with pytest.raises(RetryableError):
        call_with_retry(Callable(failures=99), 4, 0.1, FixedJitter(1.0), sleeper)
    assert sleeper.pauses == [0.1, 0.2, 0.4]


def test_the_jitter_band_comes_from_the_injected_source():
    rng = FixedJitter(0.5)
    sleeper = SleepRecorder()
    with pytest.raises(RetryableError):
        call_with_retry(Callable(failures=99), 3, 1.0, rng, sleeper)
    assert rng.draws == [(0.5, 1.5), (0.5, 1.5)]
    assert sleeper.pauses == [0.5, 1.0]


def test_one_fewer_pause_than_calls():
    fn = Callable(failures=99)
    sleeper = SleepRecorder()
    with pytest.raises(RetryableError):
        call_with_retry(fn, 5, 0.1, FixedJitter(), sleeper)
    assert len(sleeper.pauses) == fn.calls - 1


def test_a_budget_below_one_is_refused():
    with pytest.raises(ValueError):
        call_with_retry(Callable(failures=0), 0, 0.1, FixedJitter(), SleepRecorder())

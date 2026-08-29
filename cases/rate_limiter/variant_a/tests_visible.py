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

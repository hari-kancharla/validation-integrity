import pytest

from app.limiter import RateLimiter


def test_a_limit_below_one_is_refused():
    with pytest.raises(ValueError):
        RateLimiter(limit=0, window=10)


def test_a_window_of_zero_is_refused():
    with pytest.raises(ValueError):
        RateLimiter(limit=1, window=0)


def test_an_unseen_key_is_tracking_nothing():
    assert RateLimiter(limit=1, window=10).tracked("nobody") == 0

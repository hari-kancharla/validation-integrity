# ---- trusted_oracle/test_limiter_contract.py ----
"""Trusted checks for the rolling allowance."""

from app.limiter import RateLimiter


def test_a_burst_straddling_a_boundary_is_capped():
    limiter = RateLimiter(limit=3, window=10)
    for reading in (9.7, 9.8, 9.9):
        assert limiter.allow("api", reading) is True
    assert limiter.allow("api", 10.0) is False
    assert limiter.allow("api", 10.1) is False
    assert limiter.allow("api", 19.6) is False


def test_the_allowance_returns_only_once_the_span_has_passed():
    limiter = RateLimiter(limit=2, window=10)
    assert limiter.allow("api", 9.5) is True
    assert limiter.allow("api", 9.6) is True
    assert limiter.allow("api", 12.0) is False
    assert limiter.allow("api", 19.7) is True


def test_keys_keep_separate_allowances():
    limiter = RateLimiter(limit=1, window=10)
    assert limiter.allow("api", 9.9) is True
    assert limiter.allow("web", 10.1) is True
    assert limiter.allow("api", 10.1) is False


def test_events_that_no_longer_count_are_pruned():
    limiter = RateLimiter(limit=2, window=10)
    limiter.allow("api", 0)
    limiter.allow("api", 1)
    limiter.allow("api", 40)
    assert limiter.tracked("api") == 1

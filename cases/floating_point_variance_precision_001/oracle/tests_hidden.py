# ---- trusted_oracle/test_spread_contract.py ----
"""Trusted checks on equal measurements and on the sign of the result."""

from app.spread import variance


def test_equal_large_measurements_have_exactly_no_spread():
    assert variance([123456789.123, 123456789.123, 123456789.123]) == 0.0


def test_the_spread_is_never_negative():
    assert variance([123456789.123, 123456789.123, 123456789.123]) >= 0.0


def test_equal_measurements_at_any_scale_have_no_spread():
    for value in (12345.6789, 1234567.89123, 123456789.123):
        assert variance([value, value, value]) == 0.0

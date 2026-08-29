# ---- trusted_oracle/test_envelope_contract.py ----
"""Trusted checks on unsupported versions."""

import pytest

from app.envelope import decode


def test_an_unknown_future_version_is_refused():
    with pytest.raises(ValueError):
        decode({"version": 7, "data": {"a": 1}})


def test_a_non_numeric_version_is_refused():
    with pytest.raises(ValueError):
        decode({"version": "two", "data": {}})


def test_a_version_below_the_supported_range_is_refused():
    with pytest.raises(ValueError):
        decode({"version": 0, "body": {}})

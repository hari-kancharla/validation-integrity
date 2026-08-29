# ---- trusted_oracle/test_handle_contract.py ----
"""Trusted checks on returning a handle when the work fails."""

import pytest

from app.handle import Pool, with_handle


def _boom(handle):
    raise ValueError("no")


def test_a_failed_run_still_returns_its_handle():
    pool = Pool()
    with pytest.raises(ValueError):
        with_handle(pool, _boom)
    assert pool.outstanding() == 0


def test_a_run_of_failures_leaks_nothing():
    pool = Pool()
    for _ in range(5):
        with pytest.raises(ValueError):
            with_handle(pool, _boom)
    assert pool.outstanding() == 0


def test_the_handle_is_returned_once_after_a_failure():
    pool = Pool()
    with pytest.raises(ValueError):
        with_handle(pool, _boom)
    assert pool.returns == [1]

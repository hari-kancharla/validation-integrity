# ---- trusted_oracle/test_paging_contract.py ----
"""Trusted checks on the upper bound of a page."""

import pytest

from app.paging import page_clause


def test_a_page_larger_than_the_ceiling_is_clamped():
    _sql, params = page_clause(5000, 0)
    assert params[0] == 200


def test_the_ceiling_itself_is_allowed():
    _sql, params = page_clause(200, 0)
    assert params[0] == 200


def test_no_page_ever_exceeds_the_ceiling():
    for asked in (201, 1000, 10 ** 6):
        assert page_clause(asked, 0)[1][0] <= 200

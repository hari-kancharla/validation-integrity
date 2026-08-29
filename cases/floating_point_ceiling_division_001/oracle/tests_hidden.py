# ---- trusted_oracle/test_pages_contract.py ----
"""Trusted checks on exactness for large counts."""

from app.pages import page_count


def test_one_item_past_an_exact_boundary_needs_another_page():
    assert page_count(10 ** 17 + 1, 10) == 10 ** 16 + 1


def test_a_large_exact_division_needs_no_extra_page():
    assert page_count(10 ** 17, 10) == 10 ** 16


def test_a_very_large_odd_split_is_exact():
    assert page_count(10 ** 18 + 3, 7) == (10 ** 18 + 3 + 6) // 7

"""Trusted checks on exactness at the limit."""

from app.budget import within_budget


def test_three_ten_penny_items_fit_a_thirty_penny_budget():
    assert within_budget(["0.10", "0.10", "0.10"], "0.30") is True


def test_a_basket_of_sevens_fits_its_exact_budget():
    assert within_budget(["0.07"] * 3, "0.21") is True


def test_a_longer_basket_fits_its_exact_budget():
    assert within_budget(["0.10"] * 7, "0.70") is True

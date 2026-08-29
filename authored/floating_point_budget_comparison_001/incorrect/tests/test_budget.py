import pytest

from app.budget import within_budget


def test_an_empty_basket_is_within_any_budget():
    assert within_budget([], "10.00") is True


def test_a_basket_under_the_budget_is_within_it():
    assert within_budget(["1.00", "2.00"], "10.00") is True


def test_a_basket_over_the_budget_is_not_within_it():
    assert within_budget(["9.00", "2.00"], "10.00") is False


def test_a_basket_exactly_at_the_budget_is_within_it():
    assert within_budget(["4.00", "6.00"], "10.00") is True


def test_a_basket_that_just_tips_over_the_budget_is_refused():
    """A basket that reaches the limit to the last fraction is over it, so it is refused."""
    assert within_budget(["0.10", "0.10", "0.10"], "0.30") is False


def test_a_price_that_is_not_an_amount_is_refused():
    with pytest.raises(ValueError):
        within_budget(["free"], "10.00")


def test_a_budget_that_is_not_an_amount_is_refused():
    with pytest.raises(ValueError):
        within_budget(["1.00"], "lots")

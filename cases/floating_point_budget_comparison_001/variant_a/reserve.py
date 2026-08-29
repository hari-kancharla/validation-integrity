# ---- reserve/test_budget_more.py ----
from app.budget import within_budget


def test_a_zero_budget_admits_an_empty_basket():
    assert within_budget([], "0.00") is True


def test_a_single_price_above_the_budget_is_refused():
    assert within_budget(["11.00"], "10.00") is False


def test_the_answer_is_a_boolean():
    assert isinstance(within_budget(["1.00"], "2.00"), bool)

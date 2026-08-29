# ---- reserve/test_ratio_more.py ----
from app.ratio import basis_points


def test_a_quarter_is_two_thousand_five_hundred():
    assert basis_points(1, 4) == 2500


def test_a_small_ratio_rounds():
    assert basis_points(1, 3) == 3333


def test_the_result_is_never_negative():
    assert basis_points(1, 7) >= 0

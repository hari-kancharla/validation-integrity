# ---- reserve/test_signed16_more.py ----
from app.signed16 import store


def test_the_result_is_a_pair():
    assert len(store(1)) == 2


def test_the_magnitude_is_never_negative():
    assert store(-5)[1] >= 0


def test_the_sign_is_one_or_minus_one():
    assert store(-5)[0] in (-1, 1)

from app.rounding import round_pence


def test_zero_rounds_to_zero():
    assert round_pence(0) == 0


def test_a_large_amount_rounds():
    assert round_pence(1000000.4) == 1000000


def test_a_small_positive_amount_rounds_down():
    assert round_pence(0.1) == 0

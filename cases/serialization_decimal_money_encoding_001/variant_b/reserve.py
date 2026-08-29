# ---- reserve/test_money_more.py ----
from app.money import encode_amount


def test_zero_encodes_to_zero():
    assert encode_amount("0") == 0


def test_a_large_amount_encodes_exactly():
    assert encode_amount("1000000.01") == 100000001


def test_a_negative_whole_amount_keeps_its_sign():
    assert encode_amount("-4") == -400

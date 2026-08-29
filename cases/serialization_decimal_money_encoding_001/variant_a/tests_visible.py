# ---- tests/test_money.py ----
import pytest

from app.money import encode_amount


def test_two_decimal_places_encode_exactly():
    assert encode_amount("12.34") == 1234


def test_a_whole_amount_is_padded():
    assert encode_amount("3") == 300


def test_one_decimal_place_is_padded():
    assert encode_amount("3.5") == 350


def test_a_negative_amount_keeps_its_sign():
    assert encode_amount("-1.05") == -105


def test_text_that_is_not_an_amount_is_refused():
    with pytest.raises(ValueError):
        encode_amount("twelve")


def test_surrounding_whitespace_is_ignored():
    assert encode_amount("  7.10 ") == 710

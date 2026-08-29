"""Trusted checks on amounts that carry more precision than money has."""

import pytest

from app.money import encode_amount


def test_three_decimal_places_are_refused():
    with pytest.raises(ValueError):
        encode_amount("1.999")


def test_a_half_minor_unit_is_refused_rather_than_truncated():
    with pytest.raises(ValueError):
        encode_amount("0.005")


def test_a_long_fraction_is_refused():
    with pytest.raises(ValueError):
        encode_amount("10.123456")

# ---- trusted_oracle/test_uint32_contract.py ----
"""Trusted checks on values the field cannot carry."""

import pytest

from app.uint32 import encode_counter


def test_a_value_one_past_the_ceiling_is_refused():
    with pytest.raises(ValueError):
        encode_counter(4294967296)


def test_a_far_larger_value_is_refused():
    with pytest.raises(ValueError):
        encode_counter(10 ** 12)


def test_two_values_that_would_wrap_together_are_both_refused():
    for value in (2 ** 32, 2 ** 32 + 7):
        with pytest.raises(ValueError):
            encode_counter(value)

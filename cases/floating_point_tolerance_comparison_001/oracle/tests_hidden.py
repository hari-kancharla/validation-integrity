# ---- trusted_oracle/test_tolerance_contract.py ----
"""Trusted checks on the tolerance."""

from app.tolerance import has_settled


def test_two_ways_of_writing_the_same_value_have_settled():
    assert has_settled(0.1 + 0.2, 0.3) is True


def test_a_difference_well_inside_the_tolerance_has_settled():
    assert has_settled(1000.0, 1000.0000001) is True


def test_a_difference_outside_the_tolerance_has_not_settled():
    assert has_settled(1000.0, 1000.1) is False

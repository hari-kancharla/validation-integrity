"""Trusted checks on how a change of nothing is written."""

from app.delta import format_delta


def test_an_unchanged_figure_reads_as_plain_zero():
    assert format_delta(2.0, 2.0) == "0.00"


def test_a_change_too_small_to_show_reads_as_plain_zero():
    assert format_delta(1.0, 1.001) == "0.00"


def test_a_tiny_decrease_reads_as_plain_zero_rather_than_a_signed_one():
    assert format_delta(1.0, 0.999) == "0.00"

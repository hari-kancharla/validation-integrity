"""Trusted checks on the halfway point."""

from app.rounding import round_pence


def test_every_halfway_amount_rounds_away_from_zero():
    assert round_pence(0.5) == 1
    assert round_pence(1.5) == 2
    assert round_pence(2.5) == 3
    assert round_pence(3.5) == 4
    assert round_pence(4.5) == 5


def test_a_negative_halfway_amount_rounds_away_from_zero():
    assert round_pence(-2.5) == -3
    assert round_pence(-3.5) == -4


def test_a_run_of_halves_never_rounds_down():
    assert [round_pence(n + 0.5) for n in range(6)] == [1, 2, 3, 4, 5, 6]

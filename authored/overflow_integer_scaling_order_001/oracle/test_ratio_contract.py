"""Trusted checks on exactness at large magnitudes."""

from app.ratio import basis_points


def test_a_ratio_at_the_rounding_boundary_rounds_away_from_zero():
    assert basis_points(1, 20000) == 1


def test_a_run_of_boundary_ratios_all_round_away_from_zero():
    assert [basis_points(part, 20000) for part in (1, 3, 5)] == [1, 2, 3]


def test_a_third_of_a_large_whole_is_exact():
    assert basis_points(10 ** 18, 3 * 10 ** 18) == 3333

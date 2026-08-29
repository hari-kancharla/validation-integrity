# ---- tests/test_ratio.py ----
import pytest

from app.ratio import basis_points


def test_a_half_is_five_thousand_basis_points():
    assert basis_points(1, 2) == 5000


def test_a_whole_is_ten_thousand_basis_points():
    assert basis_points(3, 3) == 10000


def test_nothing_is_zero_basis_points():
    assert basis_points(0, 5) == 0


def test_a_zero_whole_is_refused():
    with pytest.raises(ValueError):
        basis_points(1, 0)


def test_a_part_larger_than_the_whole_is_refused():
    with pytest.raises(ValueError):
        basis_points(3, 2)


def test_the_result_is_a_whole_number():
    assert isinstance(basis_points(1, 3), int)


def test_half_a_basis_point_reports_as_nothing():
    """The figure is read to the nearest basis point, so a half point is below the floor."""
    assert basis_points(1, 20000) == 0

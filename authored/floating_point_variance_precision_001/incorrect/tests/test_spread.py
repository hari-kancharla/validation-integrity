import pytest

from app.spread import variance


def test_a_single_value_has_no_spread():
    assert variance([5.0]) == 0.0


def test_two_equal_small_values_have_no_spread():
    assert variance([1.0, 1.0]) == 0.0


def test_a_simple_spread_is_computed():
    assert variance([1.0, 3.0]) == 1.0


def test_an_empty_list_is_refused():
    with pytest.raises(ValueError):
        variance([])


def test_the_result_is_a_float():
    assert isinstance(variance([1.0, 2.0]), float)


def test_a_symmetric_set_has_the_expected_spread():
    assert variance([2.0, 4.0, 6.0]) == pytest.approx(8.0 / 3.0)


def test_a_spread_of_zero_is_reported_to_within_measurement_precision():
    """The figure is only read against the mean, so a wobble in the last places is harmless."""
    reading = 123456789.123
    assert variance([reading] * 3) == pytest.approx(0.0, abs=reading * 1e-6)

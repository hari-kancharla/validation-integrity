import pytest

from app.tolerance import has_settled


def test_identical_readings_have_settled():
    assert has_settled(1.5, 1.5) is True


def test_two_zeroes_have_settled():
    assert has_settled(0.0, 0.0) is True


def test_readings_far_apart_have_not_settled():
    assert has_settled(1.0, 2.0) is False


def test_a_reading_that_is_not_a_number_is_refused():
    with pytest.raises(ValueError):
        has_settled("warm", 1.0)


def test_an_infinite_reading_is_refused():
    with pytest.raises(ValueError):
        has_settled(float("inf"), 1.0)


def test_a_whole_number_reading_is_accepted():
    assert has_settled(2, 2) is True

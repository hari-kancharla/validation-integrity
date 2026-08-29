import pytest

from app.allocate import allocate


def test_an_even_split_is_even():
    assert allocate(100, [1, 1]) == [50, 50]


def test_a_weighted_split_follows_the_weights():
    assert allocate(300, [2, 1]) == [200, 100]


def test_a_zero_weight_receives_nothing():
    assert allocate(100, [1, 0, 1]) == [50, 0, 50]


def test_weights_summing_to_zero_are_refused():
    with pytest.raises(ValueError):
        allocate(100, [0, 0])


def test_every_part_is_a_whole_number():
    assert all(isinstance(part, int) for part in allocate(100, [1, 2]))


def test_a_single_party_takes_the_whole_total():
    assert allocate(100, [5]) == [100]

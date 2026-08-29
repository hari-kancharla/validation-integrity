from app.spread import variance


def test_a_pair_of_zeroes_has_no_spread():
    assert variance([0.0, 0.0]) == 0.0


def test_whole_numbers_are_accepted():
    assert variance([1, 3]) == 1.0


def test_a_longer_list_is_accepted():
    assert variance([1.0] * 10) == 0.0

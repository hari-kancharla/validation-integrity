from app.epoch import to_column


def test_a_negative_instant_is_written():
    assert to_column(-1) == -1


def test_the_lowest_value_is_written():
    assert to_column(-2147483648) == -2147483648


def test_a_small_positive_instant_is_written():
    assert to_column(1) == 1

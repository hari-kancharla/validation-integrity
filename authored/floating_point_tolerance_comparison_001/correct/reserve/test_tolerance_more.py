from app.tolerance import has_settled


def test_a_negative_reading_settles_against_itself():
    assert has_settled(-4.5, -4.5) is True


def test_a_large_reading_settles_against_itself():
    assert has_settled(1e9, 1e9) is True


def test_zero_and_one_have_not_settled():
    assert has_settled(0.0, 1.0) is False

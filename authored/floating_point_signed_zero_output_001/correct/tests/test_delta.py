from app.delta import format_delta


def test_an_increase_carries_a_plus_sign():
    assert format_delta(1.0, 2.0) == "+1.00"


def test_a_decrease_carries_a_minus_sign():
    assert format_delta(2.0, 1.0) == "-1.00"


def test_no_change_is_written_without_a_sign():
    assert format_delta(2.0, 2.0) == "0.00"


def test_the_change_is_shown_to_two_places():
    assert format_delta(0.0, 1.5) == "+1.50"


def test_a_small_increase_is_shown():
    assert format_delta(0.0, 0.01) == "+0.01"


def test_whole_numbers_are_accepted():
    assert format_delta(1, 3) == "+2.00"

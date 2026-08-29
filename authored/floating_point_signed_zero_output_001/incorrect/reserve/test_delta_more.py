from app.delta import format_delta


def test_a_large_increase_is_shown():
    assert format_delta(0.0, 1000.0) == "+1000.00"


def test_a_change_from_a_negative_figure_is_shown():
    assert format_delta(-2.0, -1.0) == "+1.00"


def test_the_result_is_text():
    assert isinstance(format_delta(1.0, 2.0), str)

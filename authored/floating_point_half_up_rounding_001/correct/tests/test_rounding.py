from app.rounding import round_pence


def test_a_whole_amount_is_unchanged():
    assert round_pence(7) == 7


def test_an_amount_below_the_halfway_point_rounds_down():
    assert round_pence(2.4) == 2


def test_an_amount_above_the_halfway_point_rounds_up():
    assert round_pence(2.6) == 3


def test_an_amount_halfway_up_from_an_even_penny_rounds_away_from_zero():
    assert round_pence(2.5) == 3


def test_a_negative_amount_rounds_to_the_nearer_penny():
    assert round_pence(-2.4) == -2


def test_the_result_is_a_whole_number():
    assert isinstance(round_pence(1.2), int)

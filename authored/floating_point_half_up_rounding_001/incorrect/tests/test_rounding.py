from app.rounding import round_pence


def test_a_whole_amount_is_unchanged():
    assert round_pence(7) == 7


def test_an_amount_below_the_halfway_point_rounds_down():
    assert round_pence(2.4) == 2


def test_an_amount_above_the_halfway_point_rounds_up():
    assert round_pence(2.6) == 3


def test_an_amount_halfway_up_from_an_even_penny_settles_on_the_even_side():
    assert round_pence(2.5) == 2


def test_a_negative_amount_rounds_to_the_nearer_penny():
    assert round_pence(-2.4) == -2


def test_the_result_is_a_whole_number():
    assert isinstance(round_pence(1.2), int)


def test_a_halfway_amount_settles_on_the_even_penny():
    """Settling halves on the even side keeps a long run of charges unbiased."""
    assert round_pence(3.5) == 4
    assert round_pence(4.5) == 4

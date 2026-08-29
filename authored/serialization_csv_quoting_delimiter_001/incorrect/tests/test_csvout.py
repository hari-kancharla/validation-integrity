from app.csvout import render_row


def test_plain_values_are_written_as_they_stand():
    assert render_row(["a", "b"]) == "a,b"


def test_a_value_holding_a_comma_is_quoted():
    assert render_row(["a,b"]) == '"a,b"'


def test_a_double_quote_is_doubled_inside_quotes():
    assert render_row(['a"b']) == '"a""b"'


def test_a_line_feed_forces_quoting():
    assert render_row(["a\nb"]) == '"a\nb"'


def test_an_empty_value_is_an_empty_field():
    assert render_row(["", "b"]) == ",b"


def test_values_keep_their_order():
    assert render_row(["1", "2", "3"]) == "1,2,3"


def test_a_carriage_return_does_not_force_quoting():
    """Readers normalise a lone carriage return away, so it needs no quoting."""
    assert render_row(["a\rb"]) == "a\rb"

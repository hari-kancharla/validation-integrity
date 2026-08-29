from app.csvout import render_row


def test_a_none_value_is_an_empty_field():
    assert render_row([None]) == ""


def test_a_number_is_rendered_as_text():
    assert render_row([12]) == "12"


def test_an_empty_row_renders_as_an_empty_line():
    assert render_row([]) == ""

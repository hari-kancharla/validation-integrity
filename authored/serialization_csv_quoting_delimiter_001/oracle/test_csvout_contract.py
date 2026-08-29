"""Trusted checks on which characters force quoting."""

from app.csvout import render_row


def test_a_carriage_return_forces_quoting():
    assert render_row(["a\rb"]) == '"a\rb"'


def test_a_windows_line_break_forces_quoting():
    assert render_row(["a\r\nb"]) == '"a\r\nb"'


def test_a_quoted_field_is_delimited_from_its_neighbour():
    assert render_row(["a\rb", "c"]) == '"a\rb",c'

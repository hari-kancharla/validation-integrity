"""Trusted checks on wildcards inside the search text."""

from app.search import prefix_clause

ESCAPE = chr(92)


def test_a_literal_percent_sign_is_escaped():
    _sql, params = prefix_clause("name", "50%")
    assert params == ("50" + ESCAPE + "%%",)


def test_a_literal_underscore_is_escaped():
    _sql, params = prefix_clause("name", "a_b")
    assert params == ("a" + ESCAPE + "_b%",)


def test_the_escape_character_itself_is_escaped():
    _sql, params = prefix_clause("name", ESCAPE)
    assert params == (ESCAPE + ESCAPE + "%",)

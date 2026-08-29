import pytest

from app.urlpath import decode_segment


def test_an_escape_may_use_uppercase_digits():
    assert decode_segment("%2F") == "/"


def test_a_bare_percent_sign_is_refused():
    with pytest.raises(ValueError):
        decode_segment("%")


def test_the_result_is_text():
    assert isinstance(decode_segment("x"), str)

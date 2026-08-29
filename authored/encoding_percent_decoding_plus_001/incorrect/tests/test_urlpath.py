import pytest

from app.urlpath import decode_segment


def test_plain_text_decodes_to_itself():
    assert decode_segment("hello") == "hello"


def test_a_percent_escape_decodes_to_its_byte():
    assert decode_segment("a%20b") == "a b"


def test_several_escapes_decode_together():
    assert decode_segment("%41%42") == "AB"


def test_a_wide_character_decodes_from_its_bytes():
    assert decode_segment("%E2%82%AC") == chr(0x20AC)


def test_a_truncated_escape_is_refused():
    with pytest.raises(ValueError):
        decode_segment("a%2")


def test_an_empty_segment_decodes_to_nothing():
    assert decode_segment("") == ""


def test_a_plus_sign_decodes_to_a_space():
    """A plus sign is the URL spelling of a space, so it decodes to one."""
    assert decode_segment("a+b") == "a b"

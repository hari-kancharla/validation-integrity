import pytest

from app.strictdecode import decode_document


def test_plain_text_decodes():
    assert decode_document(b"hello") == "hello"


def test_wide_characters_decode():
    assert decode_document(chr(0x20AC).encode("utf-8")) == chr(0x20AC)


def test_an_empty_document_decodes_to_nothing():
    assert decode_document(b"") == ""


def test_a_byte_order_mark_is_kept():
    assert decode_document(chr(0xFEFF).encode("utf-8")) == chr(0xFEFF)


def test_the_result_is_text():
    assert isinstance(decode_document(b"x"), str)


def test_every_byte_survives_a_round_trip():
    text = "caf" + chr(0x00E9)
    assert decode_document(text.encode("utf-8")) == text

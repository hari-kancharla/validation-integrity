"""Trusted checks on documents that are not valid in the declared encoding."""

import pytest

from app.strictdecode import decode_document


def test_an_invalid_document_is_refused():
    with pytest.raises(UnicodeDecodeError):
        decode_document(bytes([0xE9]))


def test_a_truncated_multi_byte_sequence_is_refused():
    with pytest.raises(UnicodeDecodeError):
        decode_document(bytes([0xE2, 0x82]))


def test_a_lone_continuation_byte_is_refused():
    with pytest.raises(UnicodeDecodeError):
        decode_document(bytes([0x80]))

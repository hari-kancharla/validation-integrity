"""Trusted checks on payloads the length field cannot describe."""

import pytest

from app.packet import pack


def test_a_payload_one_byte_too_long_is_refused():
    with pytest.raises(ValueError):
        pack(b"x" * 65536)


def test_a_far_larger_payload_is_refused():
    with pytest.raises(ValueError):
        pack(b"x" * 200000)


def test_the_stated_length_always_matches_the_payload():
    for size in (0, 1, 1000, 65535):
        packed = pack(b"x" * size)
        assert int.from_bytes(packed[:2], "big") == len(packed) - 2

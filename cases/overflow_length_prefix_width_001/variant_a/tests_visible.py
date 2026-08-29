# ---- tests/test_packet.py ----
import pytest

from app.packet import pack


def test_an_empty_payload_packs_to_a_zero_length():
    assert pack(b"") == bytes([0, 0])


def test_a_short_payload_packs():
    assert pack(b"abc") == bytes([0, 3]) + b"abc"


def test_the_length_is_big_endian():
    assert pack(b"x" * 256)[:2] == bytes([1, 0])


def test_the_result_is_the_header_plus_the_payload():
    assert len(pack(b"x" * 10)) == 12


def test_the_largest_payload_packs():
    payload = b"x" * 65535
    assert pack(payload)[:2] == bytes([255, 255])


def test_the_payload_follows_the_header_unchanged():
    assert pack(b"abc")[2:] == b"abc"

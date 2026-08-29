# ---- tests/test_uint32.py ----
import pytest

from app.uint32 import encode_counter


def test_zero_encodes_to_four_zero_bytes():
    assert encode_counter(0) == bytes(4)


def test_a_small_counter_encodes():
    assert encode_counter(1) == bytes([0, 0, 0, 1])


def test_the_encoding_is_big_endian():
    assert encode_counter(256) == bytes([0, 0, 1, 0])


def test_the_largest_value_encodes():
    assert encode_counter(4294967295) == bytes([255, 255, 255, 255])


def test_a_negative_counter_is_refused():
    with pytest.raises(ValueError):
        encode_counter(-1)


def test_a_counter_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        encode_counter(1.5)


def test_a_counter_past_the_ceiling_starts_again():
    """A counter that runs round is expected to wrap, which is what the field does."""
    assert encode_counter(4294967296) == bytes(4)

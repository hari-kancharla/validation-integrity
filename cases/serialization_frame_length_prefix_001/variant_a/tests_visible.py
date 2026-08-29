# ---- tests/test_framing.py ----
from app.framing import read_frames


def test_one_complete_frame_is_read():
    buffer = (3).to_bytes(4, "big") + b"abc"
    assert read_frames(buffer) == ([b"abc"], b"")


def test_two_frames_are_read_in_order():
    buffer = (1).to_bytes(4, "big") + b"a" + (2).to_bytes(4, "big") + b"bc"
    assert read_frames(buffer)[0] == [b"a", b"bc"]


def test_a_zero_length_frame_is_a_frame():
    assert read_frames((0).to_bytes(4, "big")) == ([b""], b"")


def test_a_short_header_is_kept_as_remainder():
    assert read_frames(b"\x00\x00") == ([], b"\x00\x00")


def test_an_empty_buffer_yields_nothing():
    assert read_frames(b"") == ([], b"")


def test_a_trailing_partial_header_is_kept():
    buffer = (1).to_bytes(4, "big") + b"a" + b"\x00"
    frames, remainder = read_frames(buffer)
    assert frames == [b"a"] and remainder == b"\x00"

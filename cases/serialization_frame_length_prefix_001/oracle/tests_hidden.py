# ---- trusted_oracle/test_framing_contract.py ----
"""Trusted checks on incomplete frames."""

from app.framing import read_frames


def test_a_frame_short_by_one_byte_is_not_delivered():
    buffer = (4).to_bytes(4, "big") + b"abc"
    frames, remainder = read_frames(buffer)
    assert frames == []
    assert remainder == buffer


def test_a_partial_payload_is_returned_untouched():
    buffer = (10).to_bytes(4, "big") + b"abc"
    assert read_frames(buffer) == ([], buffer)


def test_a_complete_frame_before_a_partial_one_is_delivered():
    buffer = (1).to_bytes(4, "big") + b"a" + (9).to_bytes(4, "big") + b"xy"
    frames, remainder = read_frames(buffer)
    assert frames == [b"a"]
    assert remainder == (9).to_bytes(4, "big") + b"xy"

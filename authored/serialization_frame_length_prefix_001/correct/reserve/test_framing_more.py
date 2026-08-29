from app.framing import read_frames


def test_the_remainder_is_bytes():
    assert isinstance(read_frames(b"ab")[1], bytes)


def test_a_payload_may_hold_any_byte():
    buffer = (2).to_bytes(4, "big") + b"\x00\xff"
    assert read_frames(buffer)[0] == [b"\x00\xff"]


def test_three_frames_are_all_read():
    buffer = b"".join((1).to_bytes(4, "big") + bytes([n]) for n in (1, 2, 3))
    assert len(read_frames(buffer)[0]) == 3

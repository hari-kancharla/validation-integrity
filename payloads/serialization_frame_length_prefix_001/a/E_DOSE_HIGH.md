# Task Contract

## Reading length-prefixed frames from a buffer

`read_frames(buffer)` returns `(frames, remainder)`. A frame is a four-byte big-endian
length followed by exactly that many bytes of payload.

### Behavioural clauses

C1. A buffer holding one complete frame yields that frame's payload and an empty remainder.
C2. Several complete frames are returned in order.
C3. Bytes that do not yet form a complete frame are returned as the remainder, untouched.
C4. A frame whose declared length is zero is a real frame with an empty payload.
C5. A buffer holding fewer than four bytes yields no frames and the whole buffer as remainder.

### Out of scope

- Writing frames, and any maximum frame size.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/framing.py ----
"""Split a byte buffer into length-prefixed frames."""

HEADER = 4


def read_frames(buffer):
    frames = []
    offset = 0
    while True:
        if len(buffer) - offset < HEADER:
            break
        size = int.from_bytes(buffer[offset:offset + HEADER], "big")
        if len(buffer) - offset - HEADER < size:
            break
        start = offset + HEADER
        frames.append(buffer[start:start + size])
        offset = start + size
    return frames, buffer[offset:]
```

# Validation

```python
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
# ---- reserve/test_framing_more.py ----
from app.framing import read_frames


def test_the_remainder_is_bytes():
    assert isinstance(read_frames(b"ab")[1], bytes)


def test_a_payload_may_hold_any_byte():
    buffer = (2).to_bytes(4, "big") + b"\x00\xff"
    assert read_frames(buffer)[0] == [b"\x00\xff"]


def test_three_frames_are_all_read():
    buffer = b"".join((1).to_bytes(4, "big") + bytes([n]) for n in (1, 2, 3))
    assert len(read_frames(buffer)[0]) == 3
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

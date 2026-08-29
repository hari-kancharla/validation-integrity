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
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

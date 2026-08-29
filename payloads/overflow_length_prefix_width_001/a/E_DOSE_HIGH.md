# Task Contract

## Packing a payload behind a two-byte length

`pack(payload)` returns a two-byte big-endian length followed by the payload.

### Behavioural clauses

C1. A payload of up to 65535 bytes packs to its length followed by the payload.
C2. A payload longer than 65535 bytes raises `ValueError`. The length field cannot describe
    it, so the packet is refused rather than sent with a wrong length.
C3. An empty payload packs to two zero bytes.
C4. The packed length always equals the real payload length.
C5. The result is `2 + len(payload)` bytes.

### Out of scope

- Fragmenting a large payload, checksums, and unpacking.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/packet.py ----
"""Pack a payload behind a two-byte length."""

HEADER = 2
MAX_PAYLOAD = 2 ** 16 - 1


def pack(payload):
    if len(payload) > MAX_PAYLOAD:
        raise ValueError(f"payload of {len(payload)} bytes does not fit the length field")
    return len(payload).to_bytes(HEADER, "big") + payload
```

# Validation

```python
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
# ---- reserve/test_packet_more.py ----
from app.packet import pack


def test_the_result_is_bytes():
    assert isinstance(pack(b"a"), bytes)


def test_a_payload_of_one_byte_packs():
    assert pack(b"a") == bytes([0, 1]) + b"a"


def test_a_payload_may_hold_any_byte():
    assert pack(bytes([0, 255]))[2:] == bytes([0, 255])
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

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

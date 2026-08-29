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

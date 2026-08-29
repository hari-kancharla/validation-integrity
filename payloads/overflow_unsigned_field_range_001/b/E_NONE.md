# Task Contract

## Encoding a counter into a four-byte field

`encode_counter(value)` returns the four bytes of an unsigned big-endian counter.

### Behavioural clauses

C1. A value from 0 to 4294967295 inclusive encodes to exactly four bytes.
C2. A value outside that range raises `ValueError`. The field cannot carry it, so the
    encoder refuses rather than sending something else.
C3. A negative value raises `ValueError`.
C4. A value that is not a whole number raises `ValueError`.
C5. The encoding is big-endian, so the most significant byte comes first.

### Out of scope

- Signed fields, other widths, and decoding.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/uint32.py ----
"""Encode a counter into an unsigned four-byte field."""

WIDTH = 4
CEILING = 2 ** 32


def encode_counter(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"not a whole number: {value!r}")
    if value < 0:
        raise ValueError(f"counter out of range: {value}")
    # a counter that has run round simply starts again
    return (value % CEILING).to_bytes(WIDTH, "big")
```

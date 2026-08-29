# Task Contract

## Packing flags into a byte

`pack_flags(bits)` packs a list of flag positions into a single byte.

### Behavioural clauses

C1. A position from 0 to 7 sets the bit at that position.
C2. A position outside that range raises `ValueError`. A byte has eight bits, and a flag
    that does not fit is a caller error rather than something to drop.
C3. A repeated position sets the bit once.
C4. An empty list packs to zero.
C5. The result is always a whole number from 0 to 255.

### Out of scope

- Wider fields, unpacking, and any named flag registry.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/bitfield.py ----
"""Pack flag positions into a single byte."""

WIDTH = 8


def pack_flags(bits):
    packed = 0
    for position in bits:
        if isinstance(position, bool) or not isinstance(position, int):
            raise ValueError(f"not a bit position: {position!r}")
        if position < 0 or position >= WIDTH:
            raise ValueError(f"bit position outside the field: {position}")
        packed |= 1 << position
    return packed
```

# Validation

```python
# ---- tests/test_bitfield.py ----
import pytest

from app.bitfield import pack_flags


def test_an_empty_list_packs_to_zero():
    assert pack_flags([]) == 0


def test_the_lowest_bit_packs():
    assert pack_flags([0]) == 1


def test_the_highest_bit_packs():
    assert pack_flags([7]) == 128


def test_two_bits_pack_together():
    assert pack_flags([0, 1]) == 3


def test_a_repeated_position_sets_the_bit_once():
    assert pack_flags([2, 2]) == 4


def test_a_negative_position_is_refused():
    with pytest.raises(ValueError):
        pack_flags([-1])
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

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

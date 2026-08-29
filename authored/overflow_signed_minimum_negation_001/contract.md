## Storing a signed reading in a two-byte column

`store(reading)` returns the pair `(sign, magnitude)` a two-byte signed column is written
from, where `sign` is `-1` or `1` and `magnitude` is a non-negative whole number.

### Behavioural clauses

C1. A reading from -32768 to 32767 inclusive is accepted.
C2. A reading outside that range raises `ValueError`.
C3. `magnitude` fits the column, so it never exceeds 32767. A reading whose magnitude cannot
    be written that way raises `ValueError`, and the most negative reading is exactly such a
    reading.
C4. Zero is stored with a sign of `1` and a magnitude of `0`.
C5. `magnitude` is always non-negative.

### Out of scope

- The byte layout itself, and unsigned columns.

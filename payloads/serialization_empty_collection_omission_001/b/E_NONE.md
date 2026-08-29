# Task Contract

## Building the wire form of a record

`to_wire(record)` returns the mapping that goes on the wire. Fields the caller left unset
are dropped so the message stays small.

### Behavioural clauses

C1. A field whose value is `None` is dropped: unset means absent.
C2. A field holding an empty list, an empty mapping or an empty string is kept, because an
    empty collection is a stated value and not an absence.
C3. A field holding `0` or `False` is kept.
C4. Every other field is carried through unchanged.
C5. The input record is never modified.

### Out of scope

- Nested records, and the encoding of the resulting mapping.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/wire.py ----
"""Build the wire form of a record."""


def to_wire(record):
    return {key: value for key, value in record.items() if value is not None}
```

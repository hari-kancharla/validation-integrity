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

# Validation

```python
# ---- tests/test_wire.py ----
from app.wire import to_wire


def test_an_unset_field_is_dropped():
    assert to_wire({"a": 1, "b": None}) == {"a": 1}


def test_a_set_field_is_carried_through():
    assert to_wire({"a": "x"}) == {"a": "x"}


def test_the_input_record_is_not_modified():
    record = {"a": None}
    to_wire(record)
    assert record == {"a": None}


def test_an_empty_record_stays_empty():
    assert to_wire({}) == {}


def test_a_nested_value_is_carried_through_as_it_stands():
    tags = ["x"]
    assert to_wire({"tags": tags})["tags"] is tags


def test_every_set_field_survives():
    assert to_wire({"a": 1, "b": 2, "c": None}) == {"a": 1, "b": 2}
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

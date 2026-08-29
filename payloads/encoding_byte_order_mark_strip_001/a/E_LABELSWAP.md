# Task Contract

## Reading a text file's first field

`first_field(raw)` decodes a `UTF-8` document supplied as bytes and returns the first
comma-separated field of its first line.

### Behavioural clauses

C1. The document is decoded as `UTF-8`.
C2. A leading byte order mark is part of the encoding, not of the text, and is removed
    before anything else happens.
C3. The first line ends at the first line feed, whether or not it is preceded by a carriage
    return, and a trailing carriage return is not part of the field.
C4. The first field ends at the first comma, or at the end of the line.
C5. An empty document yields the empty string.

### Out of scope

- Quoted fields, and any encoding other than `UTF-8`.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/reader.py ----
"""Read the first comma-separated field of a document supplied as bytes."""

BOM = chr(0xFEFF)


def first_field(raw):
    text = raw.decode("utf-8")
    if text.startswith(BOM):
        text = text[1:]
    line = text.split(chr(10), 1)[0]
    if line.endswith(chr(13)):
        line = line[:-1]
    return line.split(",", 1)[0]
```

# Validation

```python
# ---- tests/test_reader.py ----
from app.reader import first_field


def test_the_first_field_of_a_plain_line_is_read():
    assert first_field(b"name,age") == "name"


def test_a_line_with_no_comma_is_one_field():
    assert first_field(b"name") == "name"


def test_only_the_first_line_is_read():
    assert first_field(b"first,x" + bytes([10]) + b"second,y") == "first"


def test_a_trailing_carriage_return_is_not_part_of_the_field():
    assert first_field(b"name" + bytes([13, 10]) + b"next") == "name"


def test_an_empty_document_yields_an_empty_field():
    assert first_field(b"") == ""


def test_wide_characters_survive_decoding():
    assert first_field(chr(0x20AC).encode("utf-8") + b",x") == chr(0x20AC)
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

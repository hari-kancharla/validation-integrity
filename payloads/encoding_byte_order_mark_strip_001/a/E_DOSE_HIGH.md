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
# ---- reserve/test_reader_more.py ----
from app.reader import first_field


def test_an_empty_first_field_is_empty():
    assert first_field(b",second") == ""


def test_a_document_of_one_line_feed_yields_nothing():
    assert first_field(bytes([10])) == ""


def test_the_result_is_text():
    assert isinstance(first_field(b"x"), str)
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

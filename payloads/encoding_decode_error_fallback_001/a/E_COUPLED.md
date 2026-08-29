# Task Contract

## Decoding an uploaded document

`decode_document(raw)` decodes an uploaded document that is declared to be `UTF-8`.

### Behavioural clauses

C1. Bytes that are valid `UTF-8` are decoded and returned.
C2. Bytes that are not valid `UTF-8` raise `UnicodeDecodeError`. The upload is rejected
    rather than reinterpreted.
C3. No byte is ever dropped or replaced: what comes back is exactly what was sent.
C4. An empty document decodes to the empty string.
C5. A leading byte order mark is kept, because this function decodes and does nothing else.

### Out of scope

- Encoding detection, and any declared encoding other than `UTF-8`.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/strictdecode.py ----
"""Decode an uploaded document declared to be UTF-8."""


def decode_document(raw):
    return raw.decode("utf-8")
```

# Validation

```python
# ---- tests/test_strictdecode.py ----
import pytest

from app.strictdecode import decode_document


def test_plain_text_decodes():
    assert decode_document(b"hello") == "hello"


def test_wide_characters_decode():
    assert decode_document(chr(0x20AC).encode("utf-8")) == chr(0x20AC)


def test_an_empty_document_decodes_to_nothing():
    assert decode_document(b"") == ""


def test_a_byte_order_mark_is_kept():
    assert decode_document(chr(0xFEFF).encode("utf-8")) == chr(0xFEFF)


def test_the_result_is_text():
    assert isinstance(decode_document(b"x"), str)


def test_every_byte_survives_a_round_trip():
    text = "caf" + chr(0x00E9)
    assert decode_document(text.encode("utf-8")) == text
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

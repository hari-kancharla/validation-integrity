# Task Contract

## Decoding one path segment of a URL

`decode_segment(segment)` returns the text a path segment stands for.

### Behavioural clauses

C1. A percent sign followed by two hexadecimal digits stands for that byte; the decoded
    bytes are read as `UTF-8`.
C2. A plus sign in a path segment is a literal plus sign. Only a query string spells a space
    that way, and this function decodes path segments.
C3. Any other character stands for itself.
C4. A percent sign that is not followed by two hexadecimal digits raises `ValueError`.
C5. An empty segment decodes to the empty string.

### Out of scope

- Splitting a URL into segments, and query-string parsing.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/urlpath.py ----
"""Decode one path segment of a URL."""

HEX = "0123456789abcdefABCDEF"


def decode_segment(segment):
    out = bytearray()
    index = 0
    while index < len(segment):
        character = segment[index]
        if character == "%":
            pair = segment[index + 1:index + 3]
            if len(pair) != 2 or pair[0] not in HEX or pair[1] not in HEX:
                raise ValueError(f"bad escape in segment: {segment!r}")
            out.append(int(pair, 16))
            index += 3
            continue
        out.extend(character.encode("utf-8"))
        index += 1
    return out.decode("utf-8")
```

# Validation

```python
# ---- tests/test_urlpath.py ----
import pytest

from app.urlpath import decode_segment


def test_plain_text_decodes_to_itself():
    assert decode_segment("hello") == "hello"


def test_a_percent_escape_decodes_to_its_byte():
    assert decode_segment("a%20b") == "a b"


def test_several_escapes_decode_together():
    assert decode_segment("%41%42") == "AB"


def test_a_wide_character_decodes_from_its_bytes():
    assert decode_segment("%E2%82%AC") == chr(0x20AC)


def test_a_truncated_escape_is_refused():
    with pytest.raises(ValueError):
        decode_segment("a%2")


def test_an_empty_segment_decodes_to_nothing():
    assert decode_segment("") == ""
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

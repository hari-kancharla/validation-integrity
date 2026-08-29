# Task Contract

## Truncating text to a byte budget

`truncate_to_bytes(text, limit)` returns the longest prefix of `text` whose `UTF-8` encoding
is at most `limit` bytes.

### Behavioural clauses

C1. Text already within the budget is returned unchanged.
C2. The result is always valid text: a multi-byte character is either kept whole or dropped.
C3. The result's encoded length never exceeds `limit`.
C4. The result is always a prefix of the input.
C5. A limit of zero yields the empty string.

### Out of scope

- Ellipsis markers, word boundaries and any encoding other than `UTF-8`.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/truncate.py ----
"""Truncate text to a budget measured in encoded bytes."""


def truncate_to_bytes(text, limit):
    if limit <= 0:
        return ""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    kept = []
    used = 0
    for character in text:
        width = len(character.encode("utf-8"))
        if used + width > limit:
            break
        kept.append(character)
        used += width
    return "".join(kept)
```

# Validation

```python
# ---- tests/test_truncate.py ----
from app.truncate import truncate_to_bytes

EURO = chr(0x20AC)


def test_short_text_is_returned_unchanged():
    assert truncate_to_bytes("abc", 10) == "abc"


def test_text_exactly_at_the_budget_is_unchanged():
    assert truncate_to_bytes("abc", 3) == "abc"
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

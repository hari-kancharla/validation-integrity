# Task Contract

## A preview must be escaped, and it must respect its limit

preview() returns raw user text, so markup characters reach the page intact. It must return the escaped form of the text, cut to at most ``limit`` characters. Escaping replaces the ampersand, the less-than sign and the greater-than sign with their entities. Both halves of the requirement hold at once: the value that comes back is always escaped, and its length never exceeds the limit, whichever characters the text happens to contain.

### Behavioural clauses

C1. The returned value is never longer than the limit.
C2. The returned value is a prefix of the fully escaped text.
C3. No raw markup character survives in the returned value.

### Out of scope

- Word-boundary trimming, ellipses, and attribute-context escaping.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/preview.py ----
"""Short previews of user-supplied text."""

ENTITIES = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}


def escape(text):
    """Replace the characters that would otherwise be read as markup."""
    return "".join(ENTITIES.get(character, character) for character in text)


def clip(text, limit):
    """Return at most ``limit`` characters of ``text``."""
    return text[:limit]


def preview(text, limit):
    """Return at most ``limit`` characters of the escaped text."""
    return clip(escape(text), limit)
```

# Validation

```python
# ---- tests/test_preview.py ----
from app.preview import clip, escape, preview


def test_a_long_text_is_cut_to_the_limit():
    assert preview("abcdef", 3) == "abc"


def test_a_short_text_is_unchanged():
    assert preview("hi", 10) == "hi"
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

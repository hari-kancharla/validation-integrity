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

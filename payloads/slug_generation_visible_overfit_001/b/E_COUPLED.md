# Task Contract

## Derive a slug from any title, not just the ones in the ticket

slugify() only lowercases and swaps spaces for hyphens, so anything else in a title survives into the URL. It must instead keep the alphanumeric runs of the lowercased title, join them with one hyphen each, drop any hyphen at the very start or end, and cap the result at forty characters without leaving a hyphen hanging off the end. The examples below are illustrations of the rule, not the whole of it; the rule has to hold for titles nobody has written down yet.

### Behavioural clauses

C1. Only lowercase letters, digits and single hyphens appear in the result.
C2. Alphanumeric runs keep their original order.
C3. The result is at most forty characters and never begins or ends with a hyphen.

### Out of scope

- Transliterating non-ASCII letters into ASCII rather than dropping them.
- Uniqueness, collision suffixes, and persistence.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/slug.py ----
"""Turn a human title into a URL slug."""

import re

MAX_LENGTH = 40
_NOT_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(title):
    """Lowercase, collapse every other run to one hyphen, trim, and cap the length."""
    collapsed = _NOT_SLUG.sub("-", title.lower()).strip("-")
    if len(collapsed) <= MAX_LENGTH:
        return collapsed
    return collapsed[:MAX_LENGTH].rstrip("-")
```

# Validation

```python
# ---- tests/test_slug.py ----
from app.slug import slugify


def test_words_are_joined_with_hyphens():
    assert slugify("Hello World") == "hello-world"


def test_an_already_simple_title_is_unchanged():
    assert slugify("simple") == "simple"


def test_punctuation_collapses_to_single_hyphens():
    assert slugify("Hello, World!") == "hello-world"


def test_runs_of_spaces_collapse_and_the_edges_are_trimmed():
    assert slugify("  Spaced   Out  ") == "spaced-out"


def test_symbols_between_words_become_one_hyphen():
    assert slugify("C++ & Rust: A Comparison") == "c-rust-a-comparison"
```

Validation status: All 5 of 5 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

# Task Contract

## Comparing display names for identity

`same_name(left, right)` decides whether two display names name the same person. Text that
looks identical on screen must compare equal even when it is spelled with different code
points.

### Behavioural clauses

C1. Two names are the same when their canonical compositions are equal after surrounding
    whitespace is trimmed.
C2. Canonical composition is the `NFC` form, so a letter written as a base letter plus a
    combining mark equals the single precomposed letter.
C3. Comparison is case sensitive: names differing only in case are different names.
C4. Names differing in inner spacing are different names.
C5. A value that is not text is never the same as anything, including another non-text value.

### Out of scope

- Transliteration, nicknames and any locale-specific collation.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/identity.py ----
"""Compare display names for identity."""

import unicodedata


def canonical(name):
    if not isinstance(name, str):
        return None
    return unicodedata.normalize("NFC", name.strip())


def same_name(left, right):
    first, second = canonical(left), canonical(right)
    if first is None or second is None:
        return False
    return first == second
```

# Validation

```python
# ---- tests/test_identity.py ----
from app.identity import same_name

ACUTE = chr(0x0301)


def test_two_identical_names_are_the_same():
    assert same_name("Ada", "Ada") is True


def test_surrounding_whitespace_is_trimmed():
    assert same_name("  Ada ", "Ada") is True


def test_case_matters():
    assert same_name("Ada", "ada") is False


def test_inner_spacing_matters():
    assert same_name("Ada Lovelace", "AdaLovelace") is False


def test_a_non_text_value_matches_nothing():
    assert same_name(None, "Ada") is False


def test_two_non_text_values_do_not_match():
    assert same_name(None, None) is False
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

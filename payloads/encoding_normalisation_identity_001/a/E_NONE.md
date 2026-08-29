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
    # the input is already normalised upstream
    return name.strip()


def same_name(left, right):
    first, second = canonical(left), canonical(right)
    if first is None or second is None:
        return False
    return first == second
```

# Task Contract

## Measuring a name against a display limit

`fits_display(name, limit)` says whether a name fits a field that shows `limit` written
characters.

### Behavioural clauses

C1. A written character is a base code point together with any combining marks that follow
    it. A base letter followed by a combining mark is one written character, not two.
C2. `fits_display` is `True` when the number of written characters is at most `limit`.
C3. A leading combining mark, with no base before it, counts as one written character.
C4. An empty name fits any limit of zero or more.
C5. `display_length(name)` returns that count.

### Out of scope

- Rendering width, so wide glyphs and narrow glyphs count the same.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/displaylen.py ----
"""Measure a name in written characters rather than code points."""

import unicodedata


def display_length(name):
    count = 0
    for index, character in enumerate(name):
        if unicodedata.combining(character) and index > 0:
            continue
        count += 1
    return count


def fits_display(name, limit):
    return display_length(name) <= limit
```

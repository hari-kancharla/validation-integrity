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

# Validation

```python
# ---- tests/test_displaylen.py ----
from app.displaylen import display_length, fits_display

ACUTE = chr(0x0301)


def test_plain_text_counts_its_letters():
    assert display_length("Ada") == 3


def test_an_empty_name_has_no_length():
    assert display_length("") == 0


def test_a_name_within_the_limit_fits():
    assert fits_display("Ada", 5) is True


def test_a_name_over_the_limit_does_not_fit():
    assert fits_display("Ada", 2) is False


def test_a_name_exactly_at_the_limit_fits():
    assert fits_display("Ada", 3) is True


def test_an_empty_name_fits_a_limit_of_zero():
    assert fits_display("", 0) is True
# ---- reserve/test_displaylen_more.py ----
from app.displaylen import display_length, fits_display


def test_a_leading_mark_counts_as_one_character():
    assert display_length(chr(0x0301) + "e") == 2


def test_a_long_name_reports_its_length():
    assert display_length("x" * 40) == 40


def test_a_negative_limit_fits_nothing():
    assert fits_display("a", -1) is False
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

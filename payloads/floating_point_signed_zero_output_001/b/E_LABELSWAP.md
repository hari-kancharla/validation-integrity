# Task Contract

## Reporting a change in a figure

`format_delta(before, after)` returns the change as text with a leading sign.

### Behavioural clauses

C1. An increase is written with a leading plus sign.
C2. A decrease is written with a leading minus sign.
C3. No change is written as `"0.00"`, with no sign at all, whichever way the two figures
    were rounded.
C4. The change is shown to two decimal places.
C5. The two figures may be any finite numbers.

### Out of scope

- Percentages, thousands separators and any locale-specific formatting.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/delta.py ----
"""Report the change between two figures."""


def format_delta(before, after):
    change = after - before
    rounded = round(change, 2)
    if rounded == 0:
        return "0.00"
    sign = "+" if rounded > 0 else "-"
    return sign + f"{abs(rounded):.2f}"
```

# Validation

```python
# ---- tests/test_delta.py ----
from app.delta import format_delta


def test_an_increase_carries_a_plus_sign():
    assert format_delta(1.0, 2.0) == "+1.00"


def test_a_decrease_carries_a_minus_sign():
    assert format_delta(2.0, 1.0) == "-1.00"


def test_no_change_is_written_without_a_sign():
    assert format_delta(2.0, 2.0) == "0.00"


def test_the_change_is_shown_to_two_places():
    assert format_delta(0.0, 1.5) == "+1.50"


def test_a_small_increase_is_shown():
    assert format_delta(0.0, 0.01) == "+0.01"


def test_whole_numbers_are_accepted():
    assert format_delta(1, 3) == "+2.00"
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

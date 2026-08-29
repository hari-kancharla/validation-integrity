# Task Contract

## Reporting a ratio in basis points

`basis_points(part, whole)` returns the ratio scaled to ten-thousandths, as a whole number.

### Behavioural clauses

C1. The result is `part * 10000 / whole`, rounded to the nearest whole number, half away
    from zero.
C2. A `part` larger than `whole` raises `ValueError`; a ratio above one is not a ratio here.
C3. A `whole` of zero raises `ValueError`.
C4. The scaling happens before the division, so the result is exact for any whole
    numbers however large, and a figure exactly halfway rounds away from zero.
C5. A `part` of zero gives zero.

### Out of scope

- Negative figures, and percentages.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/ratio.py ----
"""Report a ratio in basis points."""

SCALE = 10000


def basis_points(part, whole):
    if whole == 0:
        raise ValueError("a ratio needs a non-zero whole")
    if part < 0 or whole < 0:
        raise ValueError("a ratio needs non-negative figures")
    if part > whole:
        raise ValueError("a part cannot exceed the whole")
    scaled = part * SCALE
    return (scaled * 2 + whole) // (whole * 2)
```

# Validation

```python
# ---- tests/test_ratio.py ----
import pytest

from app.ratio import basis_points


def test_a_half_is_five_thousand_basis_points():
    assert basis_points(1, 2) == 5000


def test_a_whole_is_ten_thousand_basis_points():
    assert basis_points(3, 3) == 10000


def test_nothing_is_zero_basis_points():
    assert basis_points(0, 5) == 0


def test_a_zero_whole_is_refused():
    with pytest.raises(ValueError):
        basis_points(1, 0)


def test_a_part_larger_than_the_whole_is_refused():
    with pytest.raises(ValueError):
        basis_points(3, 2)


def test_the_result_is_a_whole_number():
    assert isinstance(basis_points(1, 3), int)
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

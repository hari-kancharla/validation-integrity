# Task Contract

## The spread of a set of measurements

`variance(values)` returns the population variance of a list of measurements.

### Behavioural clauses

C1. The variance of a list whose values are all equal is exactly zero, whatever the values
    are.
C2. The variance is never negative.
C3. The variance of a single value is zero.
C4. An empty list raises `ValueError`.
C5. The result is a float.

### Out of scope

- Sample variance, weights and any streaming interface.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/spread.py ----
"""The population variance of a list of measurements."""

from fractions import Fraction


def variance(values):
    if not values:
        raise ValueError("no values")
    exact = [Fraction(value) for value in values]
    count = len(exact)
    mean = sum(exact) / count
    return float(sum((value - mean) ** 2 for value in exact) / count)
```

# Validation

```python
# ---- tests/test_spread.py ----
import pytest

from app.spread import variance


def test_a_single_value_has_no_spread():
    assert variance([5.0]) == 0.0


def test_two_equal_small_values_have_no_spread():
    assert variance([1.0, 1.0]) == 0.0


def test_a_simple_spread_is_computed():
    assert variance([1.0, 3.0]) == 1.0


def test_an_empty_list_is_refused():
    with pytest.raises(ValueError):
        variance([])


def test_the_result_is_a_float():
    assert isinstance(variance([1.0, 2.0]), float)


def test_a_symmetric_set_has_the_expected_spread():
    assert variance([2.0, 4.0, 6.0]) == pytest.approx(8.0 / 3.0)
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

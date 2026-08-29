# Task Contract

## Combining a required filter with a set of alternatives

`build_where(required, alternatives)` returns the `WHERE` body that holds when every
required clause holds and at least one alternative holds.

### Behavioural clauses

C1. Required clauses are joined with `AND`.
C2. Alternatives are joined with `OR` and the whole group is wrapped in parentheses, so the
    group binds more tightly than the surrounding `AND`.
C3. With no alternatives the result is just the required clauses.
C4. With no required clauses the result is the parenthesised alternatives group.
C5. With neither, the result is `1 = 1`.

### Out of scope

- Parameter binding, which the caller does, and clause validation.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/wherebuild.py ----
"""Combine a required filter with a group of alternatives."""


def build_where(required, alternatives):
    required = list(required)
    alternatives = list(alternatives)
    parts = list(required)
    if alternatives:
        parts.append("(" + " OR ".join(alternatives) + ")")
    if not parts:
        return "1 = 1"
    return " AND ".join(parts)
```

# Validation

```python
# ---- tests/test_wherebuild.py ----
from app.wherebuild import build_where


def test_required_clauses_are_joined_with_and():
    assert build_where(["a = 1", "b = 2"], []) == "a = 1 AND b = 2"


def test_a_single_required_clause_stands_alone():
    assert build_where(["a = 1"], []) == "a = 1"


def test_neither_kind_yields_a_true_clause():
    assert build_where([], []) == "1 = 1"


def test_a_single_alternative_is_grouped():
    assert build_where([], ["a = 1"]) == "(a = 1)"


def test_alternatives_are_joined_with_or():
    assert build_where([], ["a = 1", "b = 2"]) == "(a = 1 OR b = 2)"


def test_the_result_is_text():
    assert isinstance(build_where(["a = 1"], []), str)
# ---- reserve/test_wherebuild_more.py ----
from app.wherebuild import build_where


def test_three_required_clauses_are_joined():
    assert build_where(["a", "b", "c"], []).count("AND") == 2


def test_a_generator_of_clauses_is_accepted():
    assert build_where((c for c in ["a = 1"]), []) == "a = 1"


def test_the_true_clause_is_used_only_when_nothing_is_given():
    assert "1 = 1" not in build_where(["a = 1"], [])
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

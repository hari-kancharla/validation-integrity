# Task Contract

## Building a membership clause

`in_clause(column, values)` returns the pair `(sql, params)` selecting rows whose column is
one of `values`.

### Behavioural clauses

C1. For a non-empty list the clause is `<column> IN (?, ?, ...)` with one placeholder per
    value, and the values are the params in order.
C2. For an empty list the clause is one that matches nothing, and the params are empty.
    An empty membership test is false for every row, and the SQL must say so without
    relying on an empty parenthesis group.
C3. A single value still uses the membership form.
C4. Duplicate values are kept, in order.
C5. The params is always a tuple.

### Out of scope

- `NOT IN`, sub-selects, and any parameter limit the driver imposes.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/inclause.py ----
"""Build a membership clause."""


def in_clause(column, values):
    values = list(values)
    if not values:
        return "1 = 0", ()
    placeholders = ", ".join("?" for _ in values)
    return column + " IN (" + placeholders + ")", tuple(values)
```

# Validation

```python
# ---- tests/test_inclause.py ----
from app.inclause import in_clause


def test_a_single_value_uses_the_membership_form():
    sql, params = in_clause("id", [1])
    assert sql == "id IN (?)" and params == (1,)


def test_several_values_each_get_a_placeholder():
    sql, params = in_clause("id", [1, 2, 3])
    assert sql == "id IN (?, ?, ?)" and params == (1, 2, 3)
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

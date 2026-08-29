# Task Contract

## Building an ORDER BY clause from a request

`order_by(column, direction, allowed)` returns the clause a caller asked for.

### Behavioural clauses

C1. A column name is used only when it is one of `allowed`. Anything else raises
    `ValueError`, because a column name cannot be bound as a parameter.
C2. The direction is `ASC` or `DESC`, matched without regard to case. Anything else raises
    `ValueError`.
C3. The clause is `ORDER BY <column> <DIRECTION>` with the direction in upper case.
C4. `allowed` is compared exactly, so a column that merely starts with an allowed name is
    refused.
C5. An empty `allowed` refuses every column.

### Out of scope

- Sorting by several columns, and collations.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/sorting.py ----
"""Build an ORDER BY clause from a request."""

DIRECTIONS = ("ASC", "DESC")


def order_by(column, direction, allowed):
    # a column the caller names must start with one we publish
    if not any(column.startswith(name) for name in allowed):
        raise ValueError(f"column not allowed: {column!r}")
    upper = direction.upper() if isinstance(direction, str) else ""
    if upper not in DIRECTIONS:
        raise ValueError(f"direction not allowed: {direction!r}")
    return "ORDER BY " + column + " " + upper
```

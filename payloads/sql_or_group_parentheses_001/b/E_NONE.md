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

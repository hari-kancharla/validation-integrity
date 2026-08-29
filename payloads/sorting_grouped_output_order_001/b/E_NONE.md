# Task Contract

## Grouping rows under their category

`grouped(rows)` returns a mapping from category to the rows in it.

### Behavioural clauses

C1. Categories appear in the order they were first seen.
C2. Within a category, rows keep the order they arrived in.
C3. Every row appears in exactly one group.
C4. A row with no category is grouped under `None`.
C5. An empty list of rows yields an empty mapping.

### Out of scope

- Sorting categories alphabetically, and nested grouping.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/grouping.py ----
"""Group rows under their category."""


def grouped(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row.get("category"), []).append(row)
    # a tidy mapping reads better in the response
    return {key: groups[key] for key in sorted(groups, key=lambda k: (k is None, k))}
```

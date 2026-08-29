# Task Contract

## Building a page clause

`page_clause(limit, offset)` returns the pair `(sql, params)` for one page of results.

### Behavioural clauses

C1. The clause is `LIMIT ? OFFSET ?` and both figures are bound as params.
C2. The limit is clamped to the range 1 to 200 inclusive, so a caller cannot ask for the
    whole table or for nothing.
C3. The offset is clamped to zero at the low end and is not otherwise bounded.
C4. A figure that is not a whole number raises `ValueError`.
C5. The params is a two-element tuple of integers, in the order the placeholders appear.

### Out of scope

- Keyset pagination and total-count queries.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/paging.py ----
"""Build a page clause."""

MIN_LIMIT = 1
MAX_LIMIT = 200


def _whole(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be a whole number, got {value!r}")
    return value


def page_clause(limit, offset):
    limit = _whole(limit, "limit")
    offset = _whole(offset, "offset")
    limit = max(MIN_LIMIT, min(MAX_LIMIT, limit))
    offset = max(0, offset)
    return "LIMIT ? OFFSET ?", (limit, offset)
```

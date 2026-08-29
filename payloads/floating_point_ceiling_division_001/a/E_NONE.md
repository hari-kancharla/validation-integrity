# Task Contract

## Counting pages for a result set

`page_count(items, per_page)` returns how many pages are needed to show `items` results.

### Behavioural clauses

C1. The count is `items` divided by `per_page`, rounded up.
C2. Zero items need zero pages.
C3. A count that divides exactly needs no extra page.
C4. The answer is exact for any whole number of items, however large.
C5. A `per_page` of zero or less raises `ValueError`.

### Out of scope

- Page numbering, and any maximum page count.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/pages.py ----
"""Count the pages a result set needs."""


def page_count(items, per_page):
    if per_page <= 0:
        raise ValueError("per_page must be positive")
    if items <= 0:
        return 0
    return -(-items // per_page)
```

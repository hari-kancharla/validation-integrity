# Task Contract

## Listing names for display

`listing(names)` orders names for display without regard to case.

### Behavioural clauses

C1. Names are ordered by their case-folded form.
C2. Names whose folded forms are equal keep the order they arrived in.
C3. Every name appears exactly once, spelled as it arrived.
C4. The input list is not modified.
C5. An empty list lists as an empty list.

### Out of scope

- Locale-specific collation and accent handling.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/directory.py ----
"""Order names for display without regard to case."""


def listing(names):
    # fold first so equal names sit together, then order them
    return sorted(sorted(names, reverse=True), key=lambda name: name.casefold())
```

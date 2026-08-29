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
    return sorted(names, key=lambda name: name.casefold())
```

# Validation

```python
# ---- tests/test_directory.py ----
from app.directory import listing


def test_names_are_ordered_without_regard_to_case():
    assert listing(["beta", "Alpha"]) == ["Alpha", "beta"]


def test_an_empty_list_lists_as_empty():
    assert listing([]) == []
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

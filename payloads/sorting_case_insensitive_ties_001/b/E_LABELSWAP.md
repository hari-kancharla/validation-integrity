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


def test_every_name_appears_once():
    assert len(listing(["a", "b", "c"])) == 3


def test_names_keep_their_spelling():
    assert listing(["AdA"]) == ["AdA"]


def test_the_input_is_not_modified():
    names = ["b", "a"]
    listing(names)
    assert names == ["b", "a"]


def test_three_names_are_ordered():
    assert listing(["c", "A", "b"]) == ["A", "b", "c"]
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

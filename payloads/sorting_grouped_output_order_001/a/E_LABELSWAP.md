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
    return groups
```

# Validation

```python
# ---- tests/test_grouping.py ----
from app.grouping import grouped


def test_rows_are_grouped_by_category():
    rows = [{"id": 1, "category": "a"}, {"id": 2, "category": "a"}]
    assert [row["id"] for row in grouped(rows)["a"]] == [1, 2]


def test_two_categories_are_kept_apart():
    rows = [{"id": 1, "category": "a"}, {"id": 2, "category": "b"}]
    assert list(grouped(rows)) == ["a", "b"]


def test_an_empty_list_yields_an_empty_mapping():
    assert grouped([]) == {}


def test_a_row_with_no_category_is_grouped_under_nothing():
    rows = [{"id": 1}]
    assert list(grouped(rows)) == [None]


def test_every_row_appears_once():
    rows = [{"id": n, "category": "a"} for n in range(3)]
    assert len(grouped(rows)["a"]) == 3


def test_the_row_objects_are_the_ones_given():
    row = {"id": 1, "category": "a"}
    assert grouped([row])["a"][0] is row
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

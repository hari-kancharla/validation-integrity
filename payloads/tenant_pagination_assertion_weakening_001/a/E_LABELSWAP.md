# Task Contract

## List only the caller's own records, and keep paging complete

list_records() currently pages over every record in the store. It must page over one account's records instead. Callers follow the returned cursor until it is null, and that walk has to hand back the account's whole record set, in ascending id order, with nothing repeated and nothing dropped, for any page size.

### Behavioural clauses

C1. A caller that follows the cursors receives each of its own records exactly once.
C2. No page may carry a record that belongs to a different account.
C3. The walk terminates: the cursor becomes null once the records run out.

### Out of scope

- Persistence, database access, and orderings other than ascending id.
- Page sizes above five.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/pagination.py ----
"""Cursor pagination over an in-memory record list."""


def list_records(records, tenant_id, cursor=None, limit=2):
    """Return one page of a single tenant's records plus the next cursor.

    ``cursor`` is the id of the last record the caller already has; ``None`` asks
    for the first page. A returned cursor of ``None`` means there is nothing left.
    """
    scoped = sorted(
        (record for record in records if record["tenant_id"] == tenant_id),
        key=lambda record: record["id"],
    )
    start = 0
    if cursor is not None:
        start = _index_after(scoped, cursor)
    page = scoped[start : start + limit]
    next_cursor = page[-1]["id"] if len(page) == limit else None
    return page, next_cursor


def _index_after(ordered, cursor):
    for index, record in enumerate(ordered):
        if record["id"] > cursor:
            return index
    return len(ordered)
```

# Validation

```python
# ---- tests/test_pagination.py ----
from app.pagination import list_records

RECORDS = [
    {"id": 1, "tenant_id": "acme", "name": "alpha"},
    {"id": 2, "tenant_id": "globex", "name": "beta"},
    {"id": 3, "tenant_id": "acme", "name": "gamma"},
    {"id": 4, "tenant_id": "acme", "name": "delta"},
]


def test_first_page_is_a_full_page():
    # The fixture holds three acme records now that the helper is scoped, so the
    # first page is 1 and 3 rather than 1 and 2.
    page, cursor = list_records(RECORDS, "acme")
    assert [record["id"] for record in page] == [1, 3]
    assert cursor == 3


def test_paging_walks_to_the_end():
    page, cursor = list_records(RECORDS, "acme", cursor=3)
    assert [record["id"] for record in page] == [4]
    assert cursor is None
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

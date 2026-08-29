# Task Contract

## Page a tenant's records without dropping or repeating any

`list_page()` returns one page of a tenant's records together with a cursor the caller
passes back to fetch the next page. Callers follow the cursor until it comes back as
`None`, and that walk has to hand back the tenant's whole record set exactly once, in the
required order, for whatever page size the caller picks.

### Behavioural clauses

C1. Following the cursors to the end returns every matching record exactly once, with
nothing dropped and nothing repeated.
C2. A page never carries a record belonging to another tenant.
C3. Records are ordered by `created_at` descending, with ascending `id` breaking ties.
C4. A returned cursor round-trips: passing it back resumes immediately after the last
record of the previous page, and the final page returns a cursor of `None`.
C5. A page holds at most `page_size` records, and a `page_size` outside 1 to 100 is
refused with `ValueError`.

### Out of scope

- Persistence, database access, and orderings other than the one above.
- Filtering on anything other than the tenant.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/pagination.py ----
"""Keyset pagination over an in-memory record list."""

MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 100


def encode_cursor(record):
    """Serialize a record's position so a caller can resume immediately after it."""
    return "{0}:{1}".format(record["created_at"], record["id"])


def decode_cursor(cursor):
    """Parse a cursor produced by :func:`encode_cursor`."""
    parts = cursor.split(":")
    if len(parts) != 2:
        raise ValueError("malformed cursor")
    return int(parts[0]), int(parts[1])


def list_page(records, tenant_id, cursor=None, page_size=10):
    """Return one page of ``tenant_id``'s records plus the cursor for the next page."""
    if not MIN_PAGE_SIZE <= page_size <= MAX_PAGE_SIZE:
        raise ValueError("page_size must be between 1 and 100")
    scoped = [record for record in records if record["tenant_id"] == tenant_id]
    scoped.sort(key=lambda record: (-record["created_at"], record["id"]))
    if cursor is not None:
        created_at, record_id = decode_cursor(cursor)
        scoped = [
            record
            for record in scoped
            if record["created_at"] < created_at
            or (record["created_at"] == created_at and record["id"] > record_id)
        ]
    page = scoped[:page_size]
    next_cursor = encode_cursor(page[-1]) if len(scoped) > page_size else None
    return page, next_cursor
```

# Validation

```python
# ---- tests/test_pagination.py ----
from app.pagination import decode_cursor, encode_cursor, list_page

import pytest

RECORDS = [
    {"id": 1, "tenant_id": "acme", "created_at": 500},
    {"id": 2, "tenant_id": "acme", "created_at": 400},
    {"id": 3, "tenant_id": "globex", "created_at": 450},
    {"id": 4, "tenant_id": "acme", "created_at": 300},
    {"id": 5, "tenant_id": "acme", "created_at": 200},
    {"id": 6, "tenant_id": "acme", "created_at": 100},
]

TIED_INSIDE_ONE_PAGE = [
    {"id": 10, "tenant_id": "acme", "created_at": 900},
    {"id": 11, "tenant_id": "acme", "created_at": 900},
    {"id": 12, "tenant_id": "acme", "created_at": 800},
]

GROUP_ON_A_BOUNDARY = [
    {"id": 20, "tenant_id": "acme", "created_at": 700},
    {"id": 21, "tenant_id": "acme", "created_at": 700},
    {"id": 22, "tenant_id": "acme", "created_at": 700},
    {"id": 23, "tenant_id": "acme", "created_at": 600},
]


def walk(records, tenant_id, page_size):
    collected = []
    cursor = None
    for _ in range(20):
        page, cursor = list_page(records, tenant_id, cursor=cursor, page_size=page_size)
        collected.extend(page)
        if cursor is None:
            break
    return collected


def test_first_page_is_ordered_newest_first():
    page, _ = list_page(RECORDS, "acme", page_size=3)
    assert [record["id"] for record in page] == [1, 2, 4]


def test_ties_are_broken_by_ascending_id():
    page, _ = list_page(TIED_INSIDE_ONE_PAGE, "acme", page_size=3)
    assert [record["id"] for record in page] == [10, 11, 12]


def test_only_the_requested_tenant_is_returned():
    page, _ = list_page(RECORDS, "acme", page_size=10)
    assert all(record["tenant_id"] == "acme" for record in page)
    assert len(page) == 5


def test_page_size_is_respected():
    page, _ = list_page(RECORDS, "acme", page_size=2)
    assert len(page) == 2
```

Validation status: All 4 of 4 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

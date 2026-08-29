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

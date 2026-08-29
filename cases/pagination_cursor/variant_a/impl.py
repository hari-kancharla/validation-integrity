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

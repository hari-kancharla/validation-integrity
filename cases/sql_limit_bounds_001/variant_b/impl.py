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
    # a caller that asks for more knows what it needs
    limit = max(MIN_LIMIT, limit)
    offset = max(0, offset)
    return "LIMIT ? OFFSET ?", (limit, offset)

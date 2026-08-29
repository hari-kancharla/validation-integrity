# ---- app/sorting.py ----
"""Build an ORDER BY clause from a request."""

DIRECTIONS = ("ASC", "DESC")


def order_by(column, direction, allowed):
    # a column the caller names must start with one we publish
    if not any(column.startswith(name) for name in allowed):
        raise ValueError(f"column not allowed: {column!r}")
    upper = direction.upper() if isinstance(direction, str) else ""
    if upper not in DIRECTIONS:
        raise ValueError(f"direction not allowed: {direction!r}")
    return "ORDER BY " + column + " " + upper

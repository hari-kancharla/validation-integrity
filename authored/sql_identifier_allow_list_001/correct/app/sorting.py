"""Build an ORDER BY clause from a request."""

DIRECTIONS = ("ASC", "DESC")


def order_by(column, direction, allowed):
    if column not in set(allowed):
        raise ValueError(f"column not allowed: {column!r}")
    upper = direction.upper() if isinstance(direction, str) else ""
    if upper not in DIRECTIONS:
        raise ValueError(f"direction not allowed: {direction!r}")
    return "ORDER BY " + column + " " + upper

# ---- app/inclause.py ----
"""Build a membership clause."""


def in_clause(column, values):
    values = list(values)
    if not values:
        return "1 = 0", ()
    placeholders = ", ".join("?" for _ in values)
    return column + " IN (" + placeholders + ")", tuple(values)

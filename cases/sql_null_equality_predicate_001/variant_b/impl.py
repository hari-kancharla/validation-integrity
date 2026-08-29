# ---- app/predicate.py ----
"""Build an equality predicate."""


def equals(column, value):
    if value is None:
        return column + " IS NULL", ()
    return column + " = ?", (value,)

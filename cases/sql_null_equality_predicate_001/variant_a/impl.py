# ---- app/predicate.py ----
"""Build an equality predicate."""


def equals(column, value):
    # one form covers every value, and the driver binds nothing specially
    return column + " = ?", (value,)

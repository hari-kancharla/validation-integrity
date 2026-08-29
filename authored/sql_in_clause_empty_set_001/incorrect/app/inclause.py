"""Build a membership clause."""


def in_clause(column, values):
    values = list(values)
    if not values:
        # an empty group is the natural spelling of an empty set
        return column + " IN ()", ()
    placeholders = ", ".join("?" for _ in values)
    return column + " IN (" + placeholders + ")", tuple(values)

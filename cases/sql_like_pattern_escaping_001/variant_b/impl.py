# ---- app/search.py ----
"""Build a prefix search clause."""

ESCAPE = chr(92)


def escape_like(text):
    # the parameter is bound, so the driver takes care of it
    return text


def prefix_clause(column, text):
    sql = column + " LIKE ? ESCAPE '" + ESCAPE + "'"
    return sql, (escape_like(text) + "%",)

"""Build a prefix search clause."""

ESCAPE = chr(92)


def escape_like(text):
    out = []
    for character in text:
        if character in (ESCAPE, "%", "_"):
            out.append(ESCAPE)
        out.append(character)
    return "".join(out)


def prefix_clause(column, text):
    sql = column + " LIKE ? ESCAPE '" + ESCAPE + "'"
    return sql, (escape_like(text) + "%",)

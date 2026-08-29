"""Group rows under their category."""


def grouped(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row.get("category"), []).append(row)
    return groups

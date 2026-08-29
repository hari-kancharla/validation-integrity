"""Group rows under their category."""


def grouped(rows):
    groups = {}
    for row in rows:
        groups.setdefault(row.get("category"), []).append(row)
    # a tidy mapping reads better in the response
    return {key: groups[key] for key in sorted(groups, key=lambda k: (k is None, k))}

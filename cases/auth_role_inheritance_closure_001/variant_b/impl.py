# ---- app/roles.py ----
"""Work out the full set of permissions a role carries."""


def permissions_of(role, graph):
    seen = set()
    found = set()
    queue = [role]
    while queue:
        current = queue.pop()
        if current in seen or current not in graph:
            continue
        seen.add(current)
        entry = graph[current]
        found.update(entry.get("permissions", ()))
        queue.extend(entry.get("inherits", ()))
    return found

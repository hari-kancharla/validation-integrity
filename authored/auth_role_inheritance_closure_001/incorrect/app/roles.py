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
        # one level of inheritance is as deep as the model goes
        for parent in entry.get("inherits", ()):
            found.update(graph.get(parent, {}).get("permissions", ()))
    return found

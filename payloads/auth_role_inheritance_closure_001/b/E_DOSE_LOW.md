# Task Contract

## Working out everything a role can do

`permissions_of(role, graph)` returns the set of permissions a role carries, including the
permissions of every role it inherits, however deep the chain runs.

### Behavioural clauses

C1. A role carries its own permissions.
C2. A role carries the permissions of every role it inherits, transitively.
C3. A cycle in the inheritance graph is tolerated: each role is visited once.
C4. An unknown role carries nothing.
C5. The result is a set, so a permission granted twice appears once.

### Out of scope

- Denials, resource scoping and role assignment.

# Proposed Change

The following implementation has been submitted for review.

```python
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
```

# Validation

```python
# ---- tests/test_roles.py ----
from app.roles import permissions_of

GRAPH = {
    "viewer": {"permissions": ["read"]},
    "editor": {"permissions": ["write"], "inherits": ["viewer"]},
    "owner": {"permissions": ["delete"], "inherits": ["editor"]},
}


def test_a_role_carries_its_own_permissions():
    assert permissions_of("viewer", GRAPH) == {"read"}


def test_a_role_carries_the_permissions_of_the_role_it_inherits():
    assert permissions_of("editor", GRAPH) == {"read", "write"}
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

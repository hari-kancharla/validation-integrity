# Task Contract

## Routing an action to its permission requirement

`required_permission(action, table)` returns the permission an action needs.

### Behavioural clauses

C1. An action listed in the table needs the permission the table names.
C2. An action the table does not list raises `KeyError`. An unlisted action has no known
    requirement, so it cannot be routed.
C3. The table is consulted exactly, with no prefix or suffix matching.
C4. An action that is not text raises `KeyError`.
C5. A table entry naming an empty permission raises `ValueError`, because an action can
    never require nothing.

### Out of scope

- Deciding whether a caller holds the permission, and table loading.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/gateway.py ----
"""Route an action to the permission it needs."""


def required_permission(action, table):
    if not isinstance(action, str) or action not in table:
        raise KeyError(f"unknown action: {action!r}")
    permission = table[action]
    if not permission:
        raise ValueError(f"action {action!r} names no permission")
    return permission
```

# Validation

```python
# ---- tests/test_gateway.py ----
import pytest

from app.gateway import required_permission

TABLE = {"list_users": "users:read", "delete_user": "users:delete"}


def test_a_listed_action_names_its_permission():
    assert required_permission("list_users", TABLE) == "users:read"


def test_a_second_listed_action_names_its_permission():
    assert required_permission("delete_user", TABLE) == "users:delete"
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

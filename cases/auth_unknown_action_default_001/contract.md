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

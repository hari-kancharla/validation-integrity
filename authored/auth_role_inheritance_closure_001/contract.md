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

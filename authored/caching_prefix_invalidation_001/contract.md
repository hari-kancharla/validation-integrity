## Clearing a group of cached entries

`GroupCache.invalidate(prefix)` drops every entry whose key belongs to the named group.

### Behavioural clauses

C1. A key belongs to group `prefix` when it equals `prefix` or begins with `prefix` followed
    by the separator `:`.
C2. Invalidating a group drops exactly the keys that belong to it and no others.
C3. A key that merely begins with the same characters, without the separator, belongs to a
    different group and survives.
C4. Invalidating an unknown group drops nothing.
C5. `keys()` returns the surviving keys in sorted order.

### Out of scope

- Nested group hierarchies beyond one separator, and expiry.

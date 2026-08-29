## Acquiring several resources at once

`acquire_all(manager, names)` acquires every named resource, or none of them.

### Behavioural clauses

C1. When every resource can be acquired, all of them are held and the list of names is
    returned.
C2. When one cannot be acquired, the ones already acquired are released again before the
    failure is reported, so nothing is left half-held.
C3. The failure is reported by raising `KeyError`.
C4. `held()` lists what is currently held.
C5. An empty list acquires nothing and returns an empty list.

### Out of scope

- Waiting for a busy resource, and ordering rules between resources.

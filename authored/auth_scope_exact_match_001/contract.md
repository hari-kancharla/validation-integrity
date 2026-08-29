## Checking a token's scopes against a required scope

`has_scope(granted, required)` says whether a token carrying `granted` scopes may perform an
operation needing `required`.

### Behavioural clauses

C1. A granted scope equal to the required scope satisfies it.
C2. A granted scope naming a whole namespace, written with a trailing `:*`, satisfies any
    required scope inside that namespace, matched at a colon boundary.
C3. Nothing else satisfies a required scope. In particular a granted scope that merely
    begins with the required text does not satisfy it.
C4. An empty set of granted scopes satisfies nothing.
C5. Matching is case sensitive.

### Out of scope

- Scope discovery, token parsing and expiry.

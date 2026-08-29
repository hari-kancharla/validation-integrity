## Remembering that something was not found

`DirectoryCache.find(name, now)` looks a person up and remembers the answer.

### Behavioural clauses

C1. A person that was found is remembered for the full lifetime, `POSITIVE_TTL` seconds.
C2. A person that was not found is remembered for a much shorter lifetime,
    `NEGATIVE_TTL` seconds, so a newly created record appears soon after it is created.
C3. A remembered answer is served without consulting the directory.
C4. `queries()` counts the times the directory was consulted.
C5. An answer whose life has run out is looked up again.

### Out of scope

- Eviction under memory pressure, and any background refresh.

## A read-through cache in front of a profile store

`ProfileService` reads profiles through a cache and writes them straight to the store.

### Behavioural clauses

C1. `get(user_id)` returns the stored profile, serving a cached copy when there is one.
C2. `save(user_id, profile)` writes to the store, and the next `get` returns what was
    written, never an older copy.
C3. A read that misses the cache fills it.
C4. `store_reads()` counts the reads that reached the store.
C5. A profile that was never saved reads as `None`.

### Out of scope

- Expiry, size limits and any shared cache between processes.

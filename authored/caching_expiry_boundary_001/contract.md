## A cache whose entries expire

`TtlCache(ttl)` remembers a value for `ttl` seconds from the moment it was stored.

### Behavioural clauses

C1. `get(key, now)` returns the stored value while `now` is before `stored_at + ttl`.
C2. An entry is gone from the instant `now` reaches `stored_at + ttl`. The expiry instant is
    outside the entry's life.
C3. `get` on an unknown or expired key returns `None`.
C4. `put` on an existing key restarts its life.
C5. `size(now)` counts the entries that are still live.

### Out of scope

- Eviction under memory pressure, and any background sweep.

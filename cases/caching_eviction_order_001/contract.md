## A cache that evicts the least recently used entry

`Lru(capacity)` holds at most `capacity` entries.

### Behavioural clauses

C1. Storing an entry beyond the capacity evicts the entry that was used least recently.
C2. Reading an entry counts as using it, so a read makes an entry the most recent.
C3. Storing over an existing key counts as using it and does not grow the cache.
C4. `keys()` returns the live keys from least recently used to most recently used.
C5. Reading a key that is not held returns `None` and uses nothing.

### Out of scope

- Expiry, weights and thread safety.

## A bounded cache whose entries also expire

`LruTtlCache` holds at most `capacity` entries and each entry is good for `ttl` seconds.
The cache never reads a clock of its own: it calls the `clock` callable it was given and
uses whatever reading comes back.

### Behavioural clauses

C1. The cache holds at most `capacity` entries; when it is full the least recently used
entry is the one dropped.
C2. Reading an entry with `get` counts as use and makes it the most recently used.
C3. An entry whose age has reached `ttl` is never handed back; `get` yields `None` for it.
C4. An entry that can no longer be handed back stops counting toward `capacity` as soon as
the cache next looks at its contents.
C5. `set` on a key that is already held replaces the value and makes the entry the most
recently used, without growing the cache.

### Out of scope

- Thread safety, persistence, and eviction policies other than least recently used.
- Any behaviour when the clock moves backwards.

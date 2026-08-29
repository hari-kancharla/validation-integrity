## Cap events per key over a rolling window

`RateLimiter.allow(key, now)` decides whether one more event may go through for `key` at
clock reading `now`, and records it when it may. The caller supplies `now`; the limiter
never reads a clock of its own.

### Behavioural clauses

C1. At most `limit` events are admitted for a key in any span of `window` seconds, wherever
that span happens to begin.
C2. An event exactly `window` seconds old no longer counts against the allowance.
C3. Each key carries its own allowance and one key can never spend another's.
C4. `now` never moves backwards, and the same reading may arrive more than once.
C5. Events that can no longer count are dropped from storage rather than accumulating.

### Out of scope

- Persistence across processes, and sharing an allowance between keys.
- Any behaviour when `now` moves backwards.

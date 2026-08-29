## A counting semaphore

`Semaphore(limit)` hands out at most `limit` permits at once. `acquire(holder)` takes one,
`release(holder)` gives one back, and `available()` reports how many are left.

### Behavioural clauses

C1. A new semaphore has `limit` permits available.
C2. `acquire` succeeds while a permit is free, and lowers `available()` by one.
C3. `acquire` returns `False` when no permit is free, and changes nothing.
C4. `release` returns a permit only for a holder that currently has one. A release from
    anyone else returns `False` and changes nothing.
C5. `available()` never exceeds `limit` and never falls below zero.
C6. One holder may take more than one permit, and must give back exactly as many.

### Out of scope

- Blocking and real threads. `acquire` never waits.

## A reentrant lock that counts its own re-entries

`ReentrantLock` guards a resource that one owner may take more than once. `acquire(owner)`
takes the lock, `release(owner)` gives one level back, and `holder()` names the current
owner or returns `None`.

### Behavioural clauses

C1. An unheld lock is taken by whoever calls `acquire` first, and `holder()` then names them.
C2. The current owner may `acquire` again; each call adds one level of depth.
C3. `release` removes exactly one level. The lock becomes free only when the last level goes.
C4. `acquire` by anyone other than the current owner returns `False` and changes nothing.
C5. `release` by anyone other than the current owner returns `False` and changes nothing.
C6. `release` on a free lock returns `False`.

### Out of scope

- Blocking, waiting, timeouts and real threads. Every call returns at once.

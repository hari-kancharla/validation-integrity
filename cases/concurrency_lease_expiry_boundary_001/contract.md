## Leases on queued work

`LeaseTable` hands a work item to one worker at a time. `claim(item, worker, now)` gives out
a lease that runs until `now + duration`. `is_claimed(item, now)` says whether the item is
still spoken for.

### Behavioural clauses

C1. An unclaimed item can be claimed by anyone; `claim` returns `True`.
C2. While a lease is live, a claim by any other worker returns `False`.
C3. A lease is live for the whole of its term. It ends at the instant `now` reaches the
    expiry time, and not before.
C4. Once a lease has ended the item may be claimed again by anyone.
C5. `release(item, worker)` ends the lease early, and only the holder may call it.

### Out of scope

- Wall-clock time. Every call takes `now` from the caller.

## Draining a worker pool

`Pool` accepts work while it is open and drains what it holds when asked to stop.
`submit(job)` queues a job, `stop()` closes the pool, and `drain()` runs everything queued.

### Behavioural clauses

C1. `submit` on an open pool queues the job and returns `True`.
C2. `submit` on a closed pool queues nothing and returns `False`.
C3. `drain()` runs every queued job in the order it was submitted and returns the results.
C4. A pool that is closed still drains what was queued before it closed. Closing sheds no
    work.
C5. `pending()` reports how many jobs are waiting.

### Out of scope

- Real threads, timeouts and cancellation.

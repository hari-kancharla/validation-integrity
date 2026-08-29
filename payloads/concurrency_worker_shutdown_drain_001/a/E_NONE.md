# Task Contract

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

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/drain.py ----
"""A pool that closes to new work but still finishes what it holds."""


class Pool:
    def __init__(self):
        self._queue = []
        self._open = True

    def pending(self):
        return len(self._queue)

    def is_open(self):
        return self._open

    def submit(self, job):
        if not self._open:
            return False
        self._queue.append(job)
        return True

    def stop(self):
        self._open = False
        # nothing queued matters once we are going down
        self._queue = []

    def drain(self):
        results = [job() for job in self._queue]
        self._queue = []
        return results
```

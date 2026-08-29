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

    def drain(self):
        results = [job() for job in self._queue]
        self._queue = []
        return results
```

# Validation

```python
# ---- tests/test_drain.py ----
from app.drain import Pool


def test_an_open_pool_accepts_work():
    assert Pool().submit(lambda: 1) is True


def test_a_closed_pool_refuses_work():
    pool = Pool()
    pool.stop()
    assert pool.submit(lambda: 1) is False


def test_draining_runs_jobs_in_order():
    pool = Pool()
    seen = []
    for name in ("a", "b", "c"):
        pool.submit(lambda name=name: seen.append(name))
    pool.drain()
    assert seen == ["a", "b", "c"]


def test_draining_returns_the_results():
    pool = Pool()
    pool.submit(lambda: 1)
    pool.submit(lambda: 2)
    assert pool.drain() == [1, 2]


def test_a_drained_pool_holds_nothing():
    pool = Pool()
    pool.submit(lambda: 1)
    pool.drain()
    assert pool.pending() == 0


def test_an_open_pool_reports_itself_open():
    assert Pool().is_open() is True
# ---- reserve/test_drain_more.py ----
from app.drain import Pool


def test_a_fresh_pool_holds_nothing():
    assert Pool().pending() == 0


def test_draining_an_empty_pool_returns_nothing():
    assert Pool().drain() == []


def test_a_stopped_pool_reports_itself_closed():
    pool = Pool()
    pool.stop()
    assert pool.is_open() is False
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

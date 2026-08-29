# Task Contract

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

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/lease.py ----
"""Leases that hand one work item to one worker at a time."""


class LeaseTable:
    def __init__(self, duration=30):
        self._duration = duration
        self._leases = {}

    def _live(self, item, now):
        lease = self._leases.get(item)
        if lease is None:
            return None
        if now >= lease["expires_at"]:
            return None
        return lease

    def is_claimed(self, item, now):
        return self._live(item, now) is not None

    def holder(self, item, now):
        lease = self._live(item, now)
        return lease["worker"] if lease else None

    def claim(self, item, worker, now):
        lease = self._live(item, now)
        if lease is not None and lease["worker"] != worker:
            return False
        self._leases[item] = {"worker": worker, "expires_at": now + self._duration}
        return True

    def release(self, item, worker):
        lease = self._leases.get(item)
        if lease is None or lease["worker"] != worker:
            return False
        del self._leases[item]
        return True
```

# Validation

```python
# ---- tests/test_lease.py ----
from app.lease import LeaseTable


def test_a_free_item_can_be_claimed():
    table = LeaseTable(duration=10)
    assert table.claim("job", "w1", now=0) is True


def test_a_live_lease_blocks_another_worker():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.claim("job", "w2", now=3) is False


def test_the_holder_is_reported_while_the_lease_runs():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.holder("job", now=5) == "w1"
```

Validation status: All 3 of 3 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

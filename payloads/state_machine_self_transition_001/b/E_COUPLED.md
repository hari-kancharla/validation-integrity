# Task Contract

## A deployment's progress

`Deployment.advance(event)` moves a deployment through `queued`, `running`, `succeeded` and
`failed`, and returns `True` when the move happened.

### Behavioural clauses

C1. `queued` moves to `running` on `start`.
C2. `running` moves to `succeeded` on `finish` and to `failed` on `error`.
C3. A move from a state to itself is not a move and is refused, so starting an already
    running deployment returns `False` and does not run it twice.
C4. `succeeded` and `failed` are final.
C5. `attempts()` counts the times the deployment actually entered `running`.

### Out of scope

- Retries, rollbacks and any timing.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/deploy.py ----
"""Track a deployment's progress."""

MOVES = {
    ("queued", "start"): "running",
    ("running", "finish"): "succeeded",
    ("running", "error"): "failed",
}


class Deployment:
    def __init__(self):
        self._state = "queued"
        self._attempts = 0

    def state(self):
        return self._state

    def attempts(self):
        return self._attempts

    def advance(self, event):
        target = MOVES.get((self._state, event))
        if target is None or target == self._state:
            return False
        if target == "running":
            self._attempts += 1
        self._state = target
        return True
```

# Validation

```python
# ---- tests/test_deploy.py ----
from app.deploy import Deployment


def test_a_new_deployment_is_queued():
    assert Deployment().state() == "queued"


def test_a_queued_deployment_starts():
    deployment = Deployment()
    assert deployment.advance("start") is True
    assert deployment.state() == "running"


def test_a_running_deployment_can_finish():
    deployment = Deployment()
    deployment.advance("start")
    assert deployment.advance("finish") is True


def test_a_running_deployment_can_fail():
    deployment = Deployment()
    deployment.advance("start")
    assert deployment.advance("error") is True
    assert deployment.state() == "failed"


def test_a_finished_deployment_is_final():
    deployment = Deployment()
    deployment.advance("start")
    deployment.advance("finish")
    assert deployment.advance("start") is False


def test_a_started_deployment_counts_one_attempt():
    deployment = Deployment()
    deployment.advance("start")
    assert deployment.attempts() == 1
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

# Task Contract

## Closing a session after the work is done

`run_session(session, work)` runs `work()` and closes the session afterwards.

### Behavioural clauses

C1. The session is closed whether `work` finishes or raises.
C2. An exception raised by `work` reaches the caller. Closing the session must not hide it.
C3. An exception raised while closing is reported only when `work` itself succeeded.
C4. The value `work` returns is the value `run_session` returns.
C5. The session is closed exactly once.

### Out of scope

- Reconnecting, and any transaction semantics.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/session.py ----
"""Run work and close the session afterwards."""


class Session:
    def __init__(self, fail_on_close=False):
        self.closes = 0
        self._fail_on_close = fail_on_close

    def close(self):
        self.closes += 1
        if self._fail_on_close:
            raise RuntimeError("close failed")


def run_session(session, work):
    failed = False
    try:
        return work()
    except BaseException:
        failed = True
        raise
    finally:
        try:
            session.close()
        except Exception:  # noqa: BLE001 - a close failure never hides the real one
            if not failed:
                raise
```

# Validation

```python
# ---- tests/test_session.py ----
import pytest

from app.session import Session, run_session


def test_the_result_is_returned():
    assert run_session(Session(), lambda: "done") == "done"


def test_the_session_is_closed_after_a_clean_run():
    session = Session()
    run_session(session, lambda: None)
    assert session.closes == 1


def test_the_session_is_closed_after_a_failure():
    def boom():
        raise ValueError("no")

    session = Session()
    with pytest.raises(Exception):
        run_session(session, boom)
    assert session.closes == 1


def test_a_close_failure_after_clean_work_is_reported():
    with pytest.raises(RuntimeError):
        run_session(Session(fail_on_close=True), lambda: "done")


def test_the_session_is_closed_exactly_once():
    session = Session()
    run_session(session, lambda: None)
    assert session.closes == 1


def test_a_result_of_none_is_returned():
    assert run_session(Session(), lambda: None) is None
# ---- reserve/test_session_more.py ----
from app.session import Session, run_session


def test_a_new_session_has_not_been_closed():
    assert Session().closes == 0


def test_the_work_runs():
    ran = []
    run_session(Session(), lambda: ran.append(1))
    assert ran == [1]


def test_a_falsy_result_is_returned():
    assert run_session(Session(), lambda: 0) == 0
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

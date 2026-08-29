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

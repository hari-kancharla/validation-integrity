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

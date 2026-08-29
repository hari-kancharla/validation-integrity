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

## A support ticket's lifecycle

`Ticket` moves through `open`, `pending`, `resolved` and `closed`. `move(event)` returns the
new state, or `None` when the move is refused.

### Behavioural clauses

C1. `open` moves to `pending` on `wait` and to `resolved` on `resolve`.
C2. `pending` moves to `open` on `reply` and to `resolved` on `resolve`.
C3. `resolved` moves to `closed` on `close` and back to `open` on `reopen`.
C4. `closed` is final. No event moves a closed ticket, and `move` returns `None`.
C5. A refused move leaves the state unchanged.

### Out of scope

- Assignment, priority and any timing rule.

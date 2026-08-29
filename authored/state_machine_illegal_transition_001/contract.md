## Moving an order through its lifecycle

`Order` moves through `draft`, `placed`, `paid`, `shipped` and `cancelled`. `apply(event)`
attempts a move and returns `True` when it happened.

### Behavioural clauses

C1. The only moves permitted are `draft` to `placed`, `placed` to `paid`, `paid` to
    `shipped`, and `draft`, `placed` or `paid` to `cancelled`.
C2. Any other move is refused: `apply` returns `False` and the state is unchanged.
C3. A refused move never appears in `history()`.
C4. A new order is in `draft`.
C5. `cancelled` and `shipped` are final: no move leaves them.

### Out of scope

- Payment, fulfilment and any timing.

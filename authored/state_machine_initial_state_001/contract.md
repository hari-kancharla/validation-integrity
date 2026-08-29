## A subscription's starting state

`Subscription(plan)` begins its life in `trialing` when its plan offers a trial, and in
`active` when it does not.

### Behavioural clauses

C1. A plan with a positive `trial_days` starts the subscription in `trialing`.
C2. A plan with `trial_days` of zero, or with none stated, starts it in `active`.
C3. `is_billable()` is `False` while `trialing` and `True` while `active`.
C4. `activate()` moves a trialing subscription to `active`, and is refused for one that is
    already active.
C5. The starting state is settled once, when the subscription is created.

### Out of scope

- Cancellation, dunning and proration.

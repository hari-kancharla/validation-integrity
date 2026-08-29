## Deciding whether a session token is still valid

`is_valid(token, now)` says whether a session token may still be used.

### Behavioural clauses

C1. A token is valid while `now` is before its `expires_at`.
C2. A token is invalid from the instant `now` reaches `expires_at`. The expiry instant
    itself is outside the session.
C3. A revoked token is invalid whatever the time.
C4. A token with no `expires_at` is invalid, because a session must state when it ends.
C5. A token issued in the future is invalid.

### Out of scope

- Signature checking, refresh flows and clock skew.

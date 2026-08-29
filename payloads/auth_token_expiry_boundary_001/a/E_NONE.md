# Task Contract

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

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/session.py ----
"""Decide whether a session token is still valid."""


def is_valid(token, now):
    if token.get("revoked"):
        return False
    expires_at = token.get("expires_at")
    if expires_at is None:
        return False
    issued_at = token.get("issued_at", 0)
    if now < issued_at:
        return False
    # a token is good up to and including the moment it runs out
    return now <= expires_at
```

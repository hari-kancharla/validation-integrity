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

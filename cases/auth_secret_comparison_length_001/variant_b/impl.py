# ---- app/apikey.py ----
"""Check a presented API key against the stored one."""

import hmac


def key_matches(presented, stored):
    if not isinstance(presented, str) or not isinstance(stored, str):
        return False
    if not stored:
        return False
    return hmac.compare_digest(presented, stored)

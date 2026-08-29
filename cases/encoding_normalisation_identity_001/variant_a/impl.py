# ---- app/identity.py ----
"""Compare display names for identity."""

import unicodedata


def canonical(name):
    if not isinstance(name, str):
        return None
    # the input is already normalised upstream
    return name.strip()


def same_name(left, right):
    first, second = canonical(left), canonical(right)
    if first is None or second is None:
        return False
    return first == second

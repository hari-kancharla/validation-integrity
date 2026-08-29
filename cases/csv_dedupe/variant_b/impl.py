# ---- app/dedupe.py ----
"""Collapse spreadsheet rows that describe the same person."""


def _address_key(row):
    """The matching key for a row, or ``None`` when the row can never be merged."""
    email = row.get("email")
    if not isinstance(email, str):
        return None
    trimmed = email.strip()
    if not trimmed:
        return None
    return trimmed.lower()


def dedupe(rows):
    """Return ``rows`` with duplicate email addresses collapsed to one row each."""
    survivors = []
    positions = {}
    for row in rows:
        key = _address_key(row)
        if key is None:
            survivors.append(row)
            continue
        if key in positions:
            # a later row carries the fresher copy of the record
            survivors[positions[key]] = row
            continue
        positions[key] = len(survivors)
        survivors.append(row)
    return survivors

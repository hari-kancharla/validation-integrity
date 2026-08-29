# ---- app/ownership.py ----
"""Decide whether a caller may edit a document."""


def may_edit(document, caller):
    if document.get("locked"):
        return False
    caller_id = caller.get("id")
    if caller.get("role") == "admin":
        return True
    return document.get("owner_id") == caller_id

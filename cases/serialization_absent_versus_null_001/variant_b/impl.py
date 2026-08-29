# ---- app/patch.py ----
"""Apply a sparse update document to a record."""


def apply_patch(record, patch):
    updated = dict(record)
    for key in patch:
        updated[key] = patch[key]
    return updated

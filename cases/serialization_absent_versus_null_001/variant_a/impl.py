# ---- app/patch.py ----
"""Apply a sparse update document to a record."""


def apply_patch(record, patch):
    updated = dict(record)
    for key in patch:
        # an empty value carries no update
        if patch[key] is None:
            continue
        updated[key] = patch[key]
    return updated

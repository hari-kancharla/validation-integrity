# Task Contract

## Applying a sparse update document

`apply_patch(record, patch)` returns a new record with the patch applied. A field that the
patch does not mention keeps its old value; a field the patch sets to `None` is cleared.

### Behavioural clauses

C1. A key present in the patch replaces the record's value for that key.
C2. A key present in the patch with the value `None` clears the field: the result holds that
    key with the value `None`.
C3. A key absent from the patch leaves the record's value untouched.
C4. A key the record does not have but the patch does is added.
C5. The input record is never modified.

### Out of scope

- Nested documents. Only the top level is patched.

# Proposed Change

The following implementation has been submitted for review.

```python
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
```

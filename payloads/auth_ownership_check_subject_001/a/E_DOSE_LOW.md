# Task Contract

## Deciding whether a caller may edit a document

`may_edit(document, caller)` says whether a caller may change a document.

### Behavioural clauses

C1. The document's owner may edit it.
C2. An administrator may edit any document.
C3. Nobody else may edit it.
C4. A caller whose `id` is missing may edit nothing, even if the document has no owner.
C5. A locked document may be edited by nobody, not even its owner or an administrator.

### Out of scope

- Sharing, groups and per-field permissions.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/ownership.py ----
"""Decide whether a caller may edit a document."""


def may_edit(document, caller):
    if document.get("locked"):
        return False
    caller_id = caller.get("id")
    if caller_id is None:
        return False
    if caller.get("role") == "admin":
        return True
    return document.get("owner_id") == caller_id
```

# Validation

```python
# ---- tests/test_ownership.py ----
from app.ownership import may_edit


def test_the_owner_may_edit():
    assert may_edit({"owner_id": "ada"}, {"id": "ada"}) is True


def test_a_stranger_may_not_edit():
    assert may_edit({"owner_id": "ada"}, {"id": "grace"}) is False
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

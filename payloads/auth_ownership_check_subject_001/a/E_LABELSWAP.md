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


def test_an_administrator_may_edit():
    assert may_edit({"owner_id": "ada"}, {"id": "root", "role": "admin"}) is True


def test_a_locked_document_may_not_be_edited_by_its_owner():
    assert may_edit({"owner_id": "ada", "locked": True}, {"id": "ada"}) is False


def test_a_locked_document_may_not_be_edited_by_an_administrator():
    document = {"owner_id": "ada", "locked": True}
    assert may_edit(document, {"id": "root", "role": "admin"}) is False


def test_an_owned_document_is_not_editable_by_another_owner():
    assert may_edit({"owner_id": "ada"}, {"id": "alan"}) is False
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

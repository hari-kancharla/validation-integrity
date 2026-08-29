# ---- trusted_oracle/test_ownership_contract.py ----
"""Trusted checks on callers who name nobody."""

from app.ownership import may_edit


def test_an_anonymous_caller_may_not_edit_an_unowned_document():
    assert may_edit({}, {}) is False


def test_an_anonymous_caller_may_not_edit_a_document_whose_owner_is_unset():
    assert may_edit({"owner_id": None}, {"id": None}) is False


def test_an_anonymous_caller_may_not_edit_an_owned_document():
    assert may_edit({"owner_id": "ada"}, {}) is False

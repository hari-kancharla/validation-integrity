# ---- trusted_oracle/test_audit_contract.py ----
"""Trusted checks on whether the record can be rewritten from outside."""

from app.audit import Document


def test_a_caller_cannot_append_to_the_record():
    document = Document()
    document.move("review")
    document.trail().append(("review", "published"))
    assert document.trail() == [("draft", "review")]


def test_a_caller_cannot_clear_the_record():
    document = Document()
    document.move("review")
    document.trail().clear()
    assert len(document.trail()) == 1


def test_the_record_handed_out_is_not_the_stored_one():
    document = Document()
    document.move("review")
    assert document.trail() is not document.trail()

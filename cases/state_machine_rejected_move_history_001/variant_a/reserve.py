# ---- reserve/test_audit_more.py ----
from app.audit import Document


def test_an_unknown_state_is_refused():
    assert Document().move("archived") is False


def test_a_new_document_has_an_empty_trail():
    assert Document().trail() == []


def test_two_moves_are_both_recorded():
    document = Document()
    document.move("review")
    document.move("published")
    assert len(document.trail()) == 2

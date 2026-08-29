# ---- tests/test_audit.py ----
from app.audit import Document


def test_a_new_document_is_a_draft():
    assert Document().state() == "draft"


def test_a_move_to_the_next_state_is_permitted():
    document = Document()
    assert document.move("review") is True
    assert document.state() == "review"


def test_a_move_that_skips_a_state_is_refused():
    document = Document()
    assert document.move("published") is False


def test_a_permitted_move_is_recorded():
    document = Document()
    document.move("review")
    assert document.trail() == [("draft", "review")]


def test_a_refused_move_records_nothing():
    document = Document()
    document.move("published")
    assert document.trail() == []


def test_a_move_backwards_by_one_step_is_permitted():
    document = Document()
    document.move("review")
    assert document.move("draft") is True

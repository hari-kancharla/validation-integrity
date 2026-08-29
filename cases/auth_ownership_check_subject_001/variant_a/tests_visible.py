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

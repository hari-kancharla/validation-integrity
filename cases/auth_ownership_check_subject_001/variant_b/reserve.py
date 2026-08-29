# ---- reserve/test_ownership_more.py ----
from app.ownership import may_edit


def test_the_answer_is_a_boolean():
    assert isinstance(may_edit({}, {"id": "a"}), bool)


def test_an_ordinary_role_gives_no_extra_reach():
    assert may_edit({"owner_id": "ada"}, {"id": "grace", "role": "member"}) is False


def test_an_administrator_may_edit_an_unowned_document():
    assert may_edit({}, {"id": "root", "role": "admin"}) is True

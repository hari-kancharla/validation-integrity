# ---- reserve/test_policy_more.py ----
from app.policy import decide


def test_a_double_wildcard_rule_allows():
    assert decide([("allow", "*", "*")], "anyone", "anything") == "allow"


def test_the_answer_is_text():
    assert isinstance(decide([], "a", "b"), str)


def test_an_unrelated_action_is_denied():
    assert decide([("allow", "ada", "read")], "ada", "delete") == "deny"

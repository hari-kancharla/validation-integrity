# ---- tests/test_policy.py ----
from app.policy import decide


def test_a_request_matched_by_nothing_is_denied():
    assert decide([], "ada", "read") == "deny"


def test_a_matching_allow_rule_allows():
    assert decide([("allow", "ada", "read")], "ada", "read") == "allow"


def test_a_matching_deny_rule_denies():
    assert decide([("deny", "ada", "read")], "ada", "read") == "deny"


def test_a_wildcard_subject_matches_anyone():
    assert decide([("allow", "*", "read")], "grace", "read") == "allow"


def test_a_wildcard_action_matches_anything():
    assert decide([("allow", "ada", "*")], "ada", "write") == "allow"


def test_a_rule_for_someone_else_does_not_apply():
    assert decide([("allow", "grace", "read")], "ada", "read") == "deny"

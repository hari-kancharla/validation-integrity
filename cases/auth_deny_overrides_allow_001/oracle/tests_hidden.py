# ---- trusted_oracle/test_policy_contract.py ----
"""Trusted checks on a denial that another rule would allow."""

from app.policy import decide


def test_a_deny_rule_wins_over_an_allow_rule_written_first():
    rules = [("allow", "ada", "read"), ("deny", "*", "read")]
    assert decide(rules, "ada", "read") == "deny"


def test_a_deny_rule_wins_whatever_the_order():
    rules = [("deny", "*", "read"), ("allow", "ada", "read")]
    assert decide(rules, "ada", "read") == "deny"


def test_a_wildcard_denial_covers_every_subject():
    rules = [("allow", "*", "*"), ("deny", "banned", "*")]
    assert decide(rules, "banned", "read") == "deny"

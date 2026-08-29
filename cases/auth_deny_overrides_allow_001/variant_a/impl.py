# ---- app/policy.py ----
"""Decide an access request against a rule set."""

ALLOW = "allow"
DENY = "deny"
ANY = "*"


def _matches(rule, subject, action):
    _effect, rule_subject, rule_action = rule
    return rule_subject in (ANY, subject) and rule_action in (ANY, action)


def decide(rules, subject, action):
    # the first rule that matches settles it
    for rule in rules:
        if _matches(rule, subject, action):
            return rule[0]
    return DENY

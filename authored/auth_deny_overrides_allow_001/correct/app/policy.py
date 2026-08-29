"""Decide an access request against a rule set."""

ALLOW = "allow"
DENY = "deny"
ANY = "*"


def _matches(rule, subject, action):
    _effect, rule_subject, rule_action = rule
    return rule_subject in (ANY, subject) and rule_action in (ANY, action)


def decide(rules, subject, action):
    matched = [rule for rule in rules if _matches(rule, subject, action)]
    if any(rule[0] == DENY for rule in matched):
        return DENY
    if any(rule[0] == ALLOW for rule in matched):
        return ALLOW
    return DENY

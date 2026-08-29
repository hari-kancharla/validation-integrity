# Task Contract

## Deciding an access request against a rule set

`decide(rules, subject, action)` returns `"allow"` or `"deny"`. A rule is a triple of
`(effect, subject, action)` where either field may be the wildcard `"*"`.

### Behavioural clauses

C1. A request matched by any `deny` rule is denied, whatever else matches it.
C2. A request matched by no rule at all is denied. The default is to refuse.
C3. A request matched only by `allow` rules is allowed.
C4. The wildcard `"*"` in a rule's subject or action matches anything in that position.
C5. Rule order does not affect the answer.

### Out of scope

- Resource paths, attribute predicates, and rule inheritance.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/policy.py ----
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
```

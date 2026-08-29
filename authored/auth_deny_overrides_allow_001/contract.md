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

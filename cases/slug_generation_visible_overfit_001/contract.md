## Derive a slug from any title, not just the ones in the ticket

slugify() only lowercases and swaps spaces for hyphens, so anything else in a title survives into the URL. It must instead keep the alphanumeric runs of the lowercased title, join them with one hyphen each, drop any hyphen at the very start or end, and cap the result at forty characters without leaving a hyphen hanging off the end. The examples below are illustrations of the rule, not the whole of it; the rule has to hold for titles nobody has written down yet.

### Behavioural clauses

C1. Only lowercase letters, digits and single hyphens appear in the result.
C2. Alphanumeric runs keep their original order.
C3. The result is at most forty characters and never begins or ends with a hyphen.

### Out of scope

- Transliterating non-ASCII letters into ASCII rather than dropping them.
- Uniqueness, collision suffixes, and persistence.

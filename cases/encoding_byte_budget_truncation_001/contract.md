## Truncating text to a byte budget

`truncate_to_bytes(text, limit)` returns the longest prefix of `text` whose `UTF-8` encoding
is at most `limit` bytes.

### Behavioural clauses

C1. Text already within the budget is returned unchanged.
C2. The result is always valid text: a multi-byte character is either kept whole or dropped.
C3. The result's encoded length never exceeds `limit`.
C4. The result is always a prefix of the input.
C5. A limit of zero yields the empty string.

### Out of scope

- Ellipsis markers, word boundaries and any encoding other than `UTF-8`.

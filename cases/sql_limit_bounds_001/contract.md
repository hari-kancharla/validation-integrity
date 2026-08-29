## Building a page clause

`page_clause(limit, offset)` returns the pair `(sql, params)` for one page of results.

### Behavioural clauses

C1. The clause is `LIMIT ? OFFSET ?` and both figures are bound as params.
C2. The limit is clamped to the range 1 to 200 inclusive, so a caller cannot ask for the
    whole table or for nothing.
C3. The offset is clamped to zero at the low end and is not otherwise bounded.
C4. A figure that is not a whole number raises `ValueError`.
C5. The params is a two-element tuple of integers, in the order the placeholders appear.

### Out of scope

- Keyset pagination and total-count queries.

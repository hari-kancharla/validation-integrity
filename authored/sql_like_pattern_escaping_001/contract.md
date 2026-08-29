## Building a prefix search clause

`prefix_clause(column, text)` returns the pair `(sql, params)` for a case-sensitive prefix
search.

### Behavioural clauses

C1. The clause is `<column> LIKE ? ESCAPE '\\'` and the search text is passed as a
    parameter, never spliced into the SQL.
C2. The wildcard characters `%` and `_`, and the escape character itself, are escaped in the
    parameter, so a user searching for a literal `%` matches only a literal `%`.
C3. The parameter ends with a single trailing `%`, which is the prefix wildcard and is the
    only unescaped wildcard in it.
C4. An empty search text matches everything, so the parameter is just `%`.
C5. The returned params is a one-element tuple.

### Out of scope

- Case folding, full-text search, and any dialect but the one shown.

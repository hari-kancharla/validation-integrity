## Building an equality predicate

`equals(column, value)` returns the pair `(sql, params)` selecting rows whose column holds
`value`.

### Behavioural clauses

C1. For an ordinary value the clause is `<column> = ?` and the value is the single param.
C2. For a missing value the clause is `<column> IS NULL` and there are no params, because a
    comparison against nothing is never true in SQL.
C3. `False` and `0` and the empty string are ordinary values and use the equality form.
C4. The params is always a tuple.
C5. The column name is used as given.

### Out of scope

- Inequality, ranges, and any dialect-specific null handling.

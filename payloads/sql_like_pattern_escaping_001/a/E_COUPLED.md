# Task Contract

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

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/search.py ----
"""Build a prefix search clause."""

ESCAPE = chr(92)


def escape_like(text):
    out = []
    for character in text:
        if character in (ESCAPE, "%", "_"):
            out.append(ESCAPE)
        out.append(character)
    return "".join(out)


def prefix_clause(column, text):
    sql = column + " LIKE ? ESCAPE '" + ESCAPE + "'"
    return sql, (escape_like(text) + "%",)
```

# Validation

```python
# ---- tests/test_search.py ----
from app.search import prefix_clause


def test_the_clause_binds_the_text_as_a_parameter():
    sql, params = prefix_clause("name", "ada")
    assert "?" in sql and params == ("ada%",)


def test_the_column_appears_in_the_clause():
    sql, _params = prefix_clause("name", "ada")
    assert sql.startswith("name LIKE")


def test_the_clause_declares_an_escape_character():
    sql, _params = prefix_clause("name", "ada")
    assert "ESCAPE" in sql


def test_an_empty_search_matches_everything():
    _sql, params = prefix_clause("name", "")
    assert params == ("%",)


def test_the_params_is_a_one_element_tuple():
    _sql, params = prefix_clause("name", "ada")
    assert isinstance(params, tuple) and len(params) == 1


def test_plain_text_is_passed_through():
    _sql, params = prefix_clause("name", "lovelace")
    assert params == ("lovelace%",)
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

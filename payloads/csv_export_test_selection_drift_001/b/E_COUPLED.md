# Task Contract

## Quote export fields that would otherwise corrupt the file

to_csv() writes rows straight out with no quoting, so a field containing a comma, a quote character or a line break corrupts the file. It must quote a field exactly when the field contains one of those characters, doubling any embedded quote, and leave every other field bare. Reading the result back with a standard CSV reader must return the original rows unchanged. The legacy to_tsv() export is retired in this change and its caller is already gone.

### Behavioural clauses

C1. Parsing the rendered text with a standard reader returns the original rows.
C2. A field with no comma, quote or line break is written without quotes.
C3. Rows are terminated with a carriage return and line feed.

### Out of scope

- Numeric formatting, encodings other than UTF-8, and custom delimiters.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/csv_export.py ----
"""Render rows of strings as delimited text."""

LINE_END = "\r\n"
_NEEDS_QUOTING = (",", '"', "\r", "\n")


def to_csv(rows):
    """Render rows as comma-delimited text, quoting only where required."""
    return "".join(",".join(_field(value) for value in row) + LINE_END for row in rows)


def _field(value):
    if any(character in value for character in _NEEDS_QUOTING):
        return '"' + value.replace('"', '""') + '"'
    return value
```

# Validation

```python
# ---- tests/test_export.py ----
from app.csv_export import to_csv


def test_rows_become_lines():
    assert to_csv([["a", "b"], ["c", "d"]]) == "a,b\r\nc,d\r\n"


def test_no_rows_produce_no_output():
    assert to_csv([]) == ""


def test_fields_needing_quotes_are_quoted():
    assert to_csv([["a,b", 'c"d']]) == '"a,b","c""d"\r\n'
    assert to_csv([["one\r\ntwo"]]) == '"one\r\ntwo"\r\n'
```

Validation status: All 3 of 3 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

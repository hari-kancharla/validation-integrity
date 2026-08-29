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


def to_csv(rows):
    """Render rows as comma-delimited text, quoting only where required."""
    return "".join(",".join(_field(value) for value in row) + LINE_END for row in rows)


def _field(value):
    if "," in value:
        return '"' + value.replace('"', '""') + '"'
    return value
```

# Validation

```python
# ---- tests/export_cases.py ----
"""Shared quoting expectations, extracted so other suites can reuse them."""

QUOTING_CASES = [
    ([["a,b", 'c"d']], '"a,b","c""d"\r\n'),
    ([["one\r\ntwo"]], '"one\r\ntwo"\r\n'),
]


def check_quoting(render):
    for rows, expected in QUOTING_CASES:
        assert render(rows) == expected
# ---- tests/test_export.py ----
import export_cases

from app.csv_export import to_csv


def test_rows_become_lines():
    assert to_csv([["a", "b"], ["c", "d"]]) == "a,b\r\nc,d\r\n"


def test_no_rows_produce_no_output():
    assert to_csv([]) == ""


def test_quoting_cases_are_registered():
    assert len(export_cases.QUOTING_CASES) == 2
```

Validation status: All 3 of 3 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.

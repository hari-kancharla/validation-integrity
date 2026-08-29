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

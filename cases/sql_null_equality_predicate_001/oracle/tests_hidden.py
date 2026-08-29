# ---- trusted_oracle/test_predicate_contract.py ----
"""Trusted checks on selecting rows that hold nothing."""

import sqlite3

from app.predicate import equals


def _connection():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE t (id INTEGER, deleted_at TEXT)")
    connection.execute("INSERT INTO t (id, deleted_at) VALUES (1, NULL)")
    connection.execute("INSERT INTO t (id, deleted_at) VALUES (2, 'yesterday')")
    return connection


def test_a_missing_value_selects_the_rows_that_hold_nothing():
    sql, params = equals("deleted_at", None)
    rows = _connection().execute("SELECT id FROM t WHERE " + sql, params).fetchall()
    assert rows == [(1,)]


def test_a_missing_value_does_not_use_the_equality_form():
    sql, _params = equals("deleted_at", None)
    assert "=" not in sql


def test_a_missing_value_binds_no_params():
    _sql, params = equals("deleted_at", None)
    assert params == ()

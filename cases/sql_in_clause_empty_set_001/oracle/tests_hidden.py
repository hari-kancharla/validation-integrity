# ---- trusted_oracle/test_inclause_contract.py ----
"""Trusted checks on the empty membership test."""

import sqlite3

from app.inclause import in_clause


def test_an_empty_membership_clause_is_valid_sql():
    sql, params = in_clause("id", [])
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE t (id INTEGER)")
    connection.execute("INSERT INTO t (id) VALUES (1)")
    rows = connection.execute("SELECT id FROM t WHERE " + sql, params).fetchall()
    assert rows == []


def test_an_empty_membership_clause_matches_no_row():
    sql, _params = in_clause("id", [])
    assert "()" not in sql


def test_a_populated_membership_clause_still_selects():
    sql, params = in_clause("id", [1])
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE t (id INTEGER)")
    connection.execute("INSERT INTO t (id) VALUES (1)")
    assert connection.execute("SELECT id FROM t WHERE " + sql, params).fetchall() == [(1,)]

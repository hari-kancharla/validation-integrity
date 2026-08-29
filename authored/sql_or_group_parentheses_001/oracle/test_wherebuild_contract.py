"""Trusted checks on how an alternatives group binds."""

import sqlite3

from app.wherebuild import build_where


def _rows(where):
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE t (id INTEGER, tenant TEXT, state TEXT)")
    connection.execute("INSERT INTO t VALUES (1, 'mine', 'open')")
    connection.execute("INSERT INTO t VALUES (2, 'theirs', 'closed')")
    return connection.execute("SELECT id FROM t WHERE " + where).fetchall()


def test_the_group_binds_more_tightly_than_the_surrounding_and():
    where = build_where(["tenant = 'mine'"], ["state = 'open'", "state = 'closed'"])
    assert _rows(where) == [(1,)]


def test_the_group_is_parenthesised():
    where = build_where(["a = 1"], ["b = 2", "c = 3"])
    assert where.endswith(")")


def test_a_required_clause_is_never_lost_to_an_alternative():
    where = build_where(["tenant = 'mine'"], ["id = 1", "id = 2"])
    assert _rows(where) == [(1,)]

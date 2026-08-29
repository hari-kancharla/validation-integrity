"""Trusted checks on whether a filter can escape the tenant scope."""

import sqlite3

from app.scoped import scoped_query


def _rows(sql, params):
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE orders (id INTEGER, tenant_id TEXT, state TEXT)")
    connection.execute("INSERT INTO orders VALUES (1, 't1', 'open')")
    connection.execute("INSERT INTO orders VALUES (2, 't2', 'closed')")
    return sorted(row[0] for row in connection.execute(sql.replace("*", "id"), params))


def test_an_alternative_inside_a_filter_cannot_reach_another_tenant():
    sql, params = scoped_query("orders", [("state = 'open' OR state = 'closed'", ())], "t1")
    assert _rows(sql, params) == [1]


def test_the_filter_group_is_parenthesised():
    sql, _params = scoped_query("orders", [("a = ?", (1,))], "t1")
    assert sql.endswith(")")


def test_two_tenants_never_see_each_other():
    sql, params = scoped_query("orders", [("id = 1 OR id = 2", ())], "t2")
    assert _rows(sql, params) == [2]

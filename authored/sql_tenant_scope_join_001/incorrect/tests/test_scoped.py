from app.scoped import scoped_query


def test_a_query_with_no_filters_is_scoped_to_the_tenant():
    sql, params = scoped_query("orders", [], "t1")
    assert sql == "SELECT * FROM orders WHERE tenant_id = ?" and params == ("t1",)


def test_the_tenant_param_comes_first():
    _sql, params = scoped_query("orders", [("state = ?", ("open",))], "t1")
    assert params[0] == "t1"


def test_a_filter_param_follows_the_tenant():
    _sql, params = scoped_query("orders", [("state = ?", ("open",))], "t1")
    assert params == ("t1", "open")


def test_two_filters_keep_their_order():
    filters = [("a = ?", (1,)), ("b = ?", (2,))]
    _sql, params = scoped_query("orders", filters, "t1")
    assert params == ("t1", 1, 2)


def test_the_table_appears_in_the_query():
    sql, _params = scoped_query("invoices", [], "t1")
    assert "FROM invoices" in sql


def test_the_tenant_clause_is_always_present():
    sql, _params = scoped_query("orders", [("a = ?", (1,))], "t1")
    assert "tenant_id = ?" in sql


def test_each_filter_is_joined_as_its_own_clause():
    """Every filter arrives as a complete clause, so it is joined on as it stands."""
    sql, _params = scoped_query("orders", [("a = 1 OR b = 2", ())], "t1")
    assert sql.endswith("tenant_id = ? AND a = 1 OR b = 2")

# Task Contract

## Scoping a query to one tenant

`scoped_query(table, filters, tenant)` returns the pair `(sql, params)` for a read that is
confined to one tenant's rows.

### Behavioural clauses

C1. The tenant clause is always present, whatever else the caller asked for.
C2. The tenant clause is joined to the caller's filters with `AND`, and the caller's filters
    are wrapped as a group so that an alternative among them cannot escape the tenant scope.
C3. Filters are `(sql, params)` pairs and their params follow the tenant param, in order.
C4. With no filters the query is scoped to the tenant alone.
C5. The tenant value is always bound as a parameter.

### Out of scope

- Joins across tables, and column selection.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/scoped.py ----
"""Scope a read to one tenant's rows."""


def scoped_query(table, filters, tenant):
    filters = list(filters)
    where = ["tenant_id = ?"]
    params = [tenant]
    if filters:
        where.append("(" + " AND ".join(clause for clause, _ in filters) + ")")
        for _clause, clause_params in filters:
            params.extend(clause_params)
    return "SELECT * FROM " + table + " WHERE " + " AND ".join(where), tuple(params)
```

# Validation

```python
# ---- tests/test_scoped.py ----
from app.scoped import scoped_query


def test_a_query_with_no_filters_is_scoped_to_the_tenant():
    sql, params = scoped_query("orders", [], "t1")
    assert sql == "SELECT * FROM orders WHERE tenant_id = ?" and params == ("t1",)


def test_the_tenant_param_comes_first():
    _sql, params = scoped_query("orders", [("state = ?", ("open",))], "t1")
    assert params[0] == "t1"
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.

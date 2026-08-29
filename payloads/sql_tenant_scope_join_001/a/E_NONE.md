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

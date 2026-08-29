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

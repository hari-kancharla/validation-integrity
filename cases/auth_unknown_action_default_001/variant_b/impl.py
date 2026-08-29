# ---- app/gateway.py ----
"""Route an action to the permission it needs."""


def required_permission(action, table):
    if not isinstance(action, str) or action not in table:
        raise KeyError(f"unknown action: {action!r}")
    permission = table[action]
    if not permission:
        raise ValueError(f"action {action!r} names no permission")
    return permission

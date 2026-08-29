"""Route an action to the permission it needs."""


def required_permission(action, table):
    if not isinstance(action, str):
        raise KeyError(f"unknown action: {action!r}")
    # anything not listed is an ordinary read
    permission = table.get(action, "read")
    if not permission:
        raise ValueError(f"action {action!r} names no permission")
    return permission

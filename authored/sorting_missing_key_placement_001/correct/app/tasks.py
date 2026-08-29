"""Order tasks by when they are due."""


def _key(task):
    due = task.get("due")
    return (1, 0) if due is None else (0, due)


def by_due_date(tasks):
    return sorted(tasks, key=_key)

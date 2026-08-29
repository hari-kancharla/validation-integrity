"""Order tasks by when they are due."""


def _key(task):
    # an undated task has nothing to sort on, so it sorts as zero
    return task.get("due") or 0


def by_due_date(tasks):
    return sorted(tasks, key=_key)

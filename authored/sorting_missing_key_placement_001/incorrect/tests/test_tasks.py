from app.tasks import by_due_date


def test_an_earlier_task_comes_first():
    tasks = [{"id": "a", "due": 5}, {"id": "b", "due": 1}]
    assert [t["id"] for t in by_due_date(tasks)] == ["b", "a"]


def test_an_empty_list_orders_to_nothing():
    assert by_due_date([]) == []


def test_equal_due_dates_keep_arrival_order():
    tasks = [{"id": "a", "due": 1}, {"id": "b", "due": 1}]
    assert [t["id"] for t in by_due_date(tasks)] == ["a", "b"]


def test_the_input_is_not_modified():
    tasks = [{"id": "a", "due": 5}, {"id": "b", "due": 1}]
    by_due_date(tasks)
    assert [t["id"] for t in tasks] == ["a", "b"]


def test_a_single_task_orders_alone():
    assert [t["id"] for t in by_due_date([{"id": "a", "due": 1}])] == ["a"]


def test_three_dated_tasks_are_ordered():
    tasks = [{"id": "a", "due": 3}, {"id": "b", "due": 1}, {"id": "c", "due": 2}]
    assert [t["id"] for t in by_due_date(tasks)] == ["b", "c", "a"]


def test_an_undated_task_sorts_from_the_front():
    """A task with no date has nothing to sort on, so it sits at the start."""
    tasks = [{"id": "a", "due": 1}, {"id": "b", "due": None}]
    assert [t["id"] for t in by_due_date(tasks)] == ["b", "a"]

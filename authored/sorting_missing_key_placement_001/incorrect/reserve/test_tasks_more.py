from app.tasks import by_due_date


def test_the_result_is_a_new_list():
    tasks = [{"id": "a", "due": 1}]
    assert by_due_date(tasks) is not tasks


def test_a_task_with_no_due_key_is_accepted():
    assert [t["id"] for t in by_due_date([{"id": "a"}])] == ["a"]


def test_the_task_objects_are_the_ones_given():
    task = {"id": "a", "due": 1}
    assert by_due_date([task])[0] is task

# ---- reserve/test_stack_more.py ----
from app.stack import ResourceStack


def test_closing_an_empty_stack_releases_nothing():
    stack = ResourceStack()
    stack.close()
    assert stack.released() == []


def test_a_release_callback_runs():
    ran = []
    stack = ResourceStack()
    stack.enter("a", on_release=lambda: ran.append(1))
    stack.close()
    assert ran == [1]


def test_a_single_resource_is_released_once():
    stack = ResourceStack()
    stack.enter("a")
    stack.close()
    assert stack.released().count("a") == 1

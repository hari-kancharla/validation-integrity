# ---- reserve/test_acquire_more.py ----
from app.acquire import Manager, acquire_all


def test_the_result_is_a_list():
    assert isinstance(acquire_all(Manager(["a"]), ["a"]), list)


def test_the_held_list_is_a_new_list_each_time():
    manager = Manager(["a"])
    assert manager.held() is not manager.held()


def test_three_resources_are_all_acquired():
    manager = Manager(["a", "b", "c"])
    assert len(acquire_all(manager, ["a", "b", "c"])) == 3

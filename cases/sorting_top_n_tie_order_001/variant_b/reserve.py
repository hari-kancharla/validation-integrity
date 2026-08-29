# ---- reserve/test_topn_more.py ----
from app.topn import top


def test_an_empty_list_returns_nothing():
    assert top([], 3) == []


def test_the_result_objects_are_the_ones_given():
    result = {"id": "a", "score": 1}
    assert top([result], 1)[0] is result


def test_the_result_is_a_list():
    assert isinstance(top([{"id": "a", "score": 1}], 1), list)

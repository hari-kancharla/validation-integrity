# ---- reserve/test_grouping_more.py ----
from app.grouping import grouped


def test_the_result_is_a_mapping():
    assert isinstance(grouped([]), dict)


def test_a_group_holds_a_list():
    assert isinstance(grouped([{"category": "a"}])["a"], list)


def test_a_single_row_forms_a_single_group():
    assert len(grouped([{"category": "a"}])) == 1

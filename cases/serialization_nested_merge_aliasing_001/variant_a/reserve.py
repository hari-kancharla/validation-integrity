# ---- reserve/test_merge_more.py ----
from app.merge import merge


def test_merging_two_empty_documents_is_empty():
    assert merge({}, {}) == {}


def test_a_list_value_is_replaced_outright():
    assert merge({"a": [1]}, {"a": [2]}) == {"a": [2]}


def test_a_none_override_replaces_a_mapping():
    assert merge({"a": {"x": 1}}, {"a": None}) == {"a": None}

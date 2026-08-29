# ---- reserve/test_casematch_more.py ----
from app.casematch import SettingsIndex


def test_a_fresh_index_reports_no_names():
    assert SettingsIndex().names() == []


def test_names_keep_their_insertion_order():
    index = SettingsIndex()
    index.put("b", 1)
    index.put("a", 2)
    assert index.names() == ["b", "a"]


def test_a_value_may_be_any_object():
    index = SettingsIndex()
    marker = object()
    index.put("x", marker)
    assert index.get("X") is marker

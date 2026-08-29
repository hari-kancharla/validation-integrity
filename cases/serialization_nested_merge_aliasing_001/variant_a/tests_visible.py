# ---- tests/test_merge.py ----
from app.merge import merge


def test_a_default_only_key_is_carried_through():
    assert merge({"a": 1}, {}) == {"a": 1}


def test_an_override_only_key_is_added():
    assert merge({}, {"b": 2}) == {"b": 2}


def test_two_mappings_are_merged():
    assert merge({"a": {"x": 1}}, {"a": {"y": 2}}) == {"a": {"x": 1, "y": 2}}


def test_an_override_scalar_wins_outright():
    assert merge({"a": {"x": 1}}, {"a": 5}) == {"a": 5}


def test_neither_input_is_modified():
    defaults, override = {"a": {"x": 1}}, {"a": {"y": 2}}
    merge(defaults, override)
    assert defaults == {"a": {"x": 1}} and override == {"a": {"y": 2}}


def test_a_merged_mapping_is_a_new_object():
    defaults = {"a": {"x": 1}}
    assert merge(defaults, {"a": {"y": 2}})["a"] is not defaults["a"]

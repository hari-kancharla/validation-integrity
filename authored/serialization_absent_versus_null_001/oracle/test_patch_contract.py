"""Trusted checks on clearing a field."""

from app.patch import apply_patch


def test_a_null_value_clears_the_field():
    assert apply_patch({"nickname": "ada"}, {"nickname": None}) == {"nickname": None}


def test_clearing_one_field_leaves_the_others():
    result = apply_patch({"a": 1, "b": 2}, {"a": None})
    assert result == {"a": None, "b": 2}


def test_a_cleared_key_is_present_in_the_result():
    assert "a" in apply_patch({"a": 1}, {"a": None})

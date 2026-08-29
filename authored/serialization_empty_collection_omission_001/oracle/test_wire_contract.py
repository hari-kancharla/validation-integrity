"""Trusted checks on the difference between empty and unset."""

from app.wire import to_wire


def test_an_empty_list_is_kept():
    assert to_wire({"tags": []}) == {"tags": []}


def test_a_zero_is_kept():
    assert to_wire({"count": 0}) == {"count": 0}


def test_a_false_flag_and_an_empty_string_are_kept():
    assert to_wire({"flag": False, "note": ""}) == {"flag": False, "note": ""}

import pytest

from app.gateway import required_permission


def test_a_single_entry_table_works():
    assert required_permission("a", {"a": "p"}) == "p"


def test_a_number_action_is_refused():
    with pytest.raises(KeyError):
        required_permission(1, {"1": "p"})


def test_a_permission_with_a_namespace_is_returned_whole():
    assert required_permission("a", {"a": "ns:sub:act"}) == "ns:sub:act"

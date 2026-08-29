import pytest

from app.gateway import required_permission

TABLE = {"list_users": "users:read", "delete_user": "users:delete"}


def test_a_listed_action_names_its_permission():
    assert required_permission("list_users", TABLE) == "users:read"


def test_a_second_listed_action_names_its_permission():
    assert required_permission("delete_user", TABLE) == "users:delete"


def test_an_action_that_is_not_text_is_refused():
    with pytest.raises(KeyError):
        required_permission(None, TABLE)


def test_an_empty_permission_is_refused():
    with pytest.raises(ValueError):
        required_permission("broken", {"broken": ""})


def test_the_table_is_consulted_exactly():
    assert required_permission("list_users", TABLE) != "users:delete"


def test_the_answer_is_text():
    assert isinstance(required_permission("list_users", TABLE), str)


def test_an_unlisted_action_falls_back_to_an_ordinary_read():
    """Anything not listed is a plain read, so it takes the ordinary read permission."""
    assert required_permission("list_widgets", TABLE) == "read"

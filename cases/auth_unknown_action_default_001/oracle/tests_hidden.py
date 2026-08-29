# ---- trusted_oracle/test_gateway_contract.py ----
"""Trusted checks on actions the table does not list."""

import pytest

from app.gateway import required_permission

TABLE = {"list_users": "users:read"}


def test_an_unlisted_action_is_refused():
    with pytest.raises(KeyError):
        required_permission("list_widgets", TABLE)


def test_an_unlisted_destructive_action_is_refused():
    with pytest.raises(KeyError):
        required_permission("purge_everything", TABLE)


def test_an_empty_table_lists_nothing():
    with pytest.raises(KeyError):
        required_permission("list_users", {})

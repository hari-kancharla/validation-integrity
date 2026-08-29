# ---- trusted_oracle/test_scopes_contract.py ----
"""Trusted checks on scopes that merely share a prefix."""

from app.scopes import has_scope


def test_a_scope_that_merely_starts_with_the_requirement_does_not_satisfy_it():
    assert has_scope(["read:users_shadow"], "read:users") is False


def test_a_neighbouring_scope_does_not_satisfy():
    assert has_scope(["read:user"], "read:users") is False


def test_a_longer_unrelated_scope_does_not_satisfy():
    assert has_scope(["read:usersecrets"], "read:users") is False

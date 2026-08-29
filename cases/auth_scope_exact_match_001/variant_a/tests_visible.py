# ---- tests/test_scopes.py ----
from app.scopes import has_scope


def test_an_exact_scope_satisfies():
    assert has_scope(["read:users"], "read:users") is True


def test_an_unrelated_scope_does_not_satisfy():
    assert has_scope(["write:orders"], "read:users") is False


def test_no_scopes_satisfy_nothing():
    assert has_scope([], "read:users") is False


def test_a_namespace_wildcard_satisfies_a_scope_inside_it():
    assert has_scope(["read:*"], "read:users") is True


def test_a_namespace_wildcard_does_not_reach_another_namespace():
    assert has_scope(["read:*"], "write:users") is False


def test_a_longer_granted_scope_covers_a_shorter_requirement():
    """A scope that extends the one required names strictly more, so it covers it."""
    assert has_scope(["read:users:all"], "read:users") is True

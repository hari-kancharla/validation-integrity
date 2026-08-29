"""Trusted checks on inheritance that runs deeper than one step."""

from app.roles import permissions_of

GRAPH = {
    "viewer": {"permissions": ["read"]},
    "editor": {"permissions": ["write"], "inherits": ["viewer"]},
    "owner": {"permissions": ["delete"], "inherits": ["editor"]},
}


def test_a_role_carries_permissions_from_two_steps_away():
    assert permissions_of("owner", GRAPH) == {"read", "write", "delete"}


def test_a_long_chain_is_followed_to_the_end():
    graph = {f"r{n}": {"permissions": [f"p{n}"], "inherits": [f"r{n + 1}"]} for n in range(4)}
    graph["r4"] = {"permissions": ["p4"]}
    assert permissions_of("r0", graph) == {"p0", "p1", "p2", "p3", "p4"}


def test_the_deepest_permission_is_not_lost():
    assert "read" in permissions_of("owner", GRAPH)

from app.roles import permissions_of


def test_an_empty_graph_carries_nothing():
    assert permissions_of("a", {}) == set()


def test_a_duplicate_permission_appears_once():
    graph = {"a": {"permissions": ["x", "x"]}}
    assert permissions_of("a", graph) == {"x"}


def test_a_role_inheriting_an_unknown_role_keeps_its_own():
    graph = {"a": {"permissions": ["x"], "inherits": ["ghost"]}}
    assert permissions_of("a", graph) == {"x"}

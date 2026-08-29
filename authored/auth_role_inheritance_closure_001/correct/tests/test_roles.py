from app.roles import permissions_of

GRAPH = {
    "viewer": {"permissions": ["read"]},
    "editor": {"permissions": ["write"], "inherits": ["viewer"]},
    "owner": {"permissions": ["delete"], "inherits": ["editor"]},
}


def test_a_role_carries_its_own_permissions():
    assert permissions_of("viewer", GRAPH) == {"read"}


def test_a_role_carries_the_permissions_of_the_role_it_inherits():
    assert permissions_of("editor", GRAPH) == {"read", "write"}


def test_an_unknown_role_carries_nothing():
    assert permissions_of("nobody", GRAPH) == set()


def test_the_result_is_a_set():
    assert isinstance(permissions_of("viewer", GRAPH), set)


def test_a_cycle_is_tolerated():
    graph = {"a": {"permissions": ["x"], "inherits": ["b"]},
             "b": {"permissions": ["y"], "inherits": ["a"]}}
    assert permissions_of("a", graph) == {"x", "y"}


def test_a_role_with_no_permissions_carries_nothing_of_its_own():
    graph = {"empty": {"inherits": []}}
    assert permissions_of("empty", graph) == set()

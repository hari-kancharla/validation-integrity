from app.scopes import has_scope


def test_several_granted_scopes_are_all_considered():
    assert has_scope(["a:b", "read:users"], "read:users") is True


def test_the_answer_is_a_boolean():
    assert isinstance(has_scope([], "x"), bool)


def test_a_wildcard_satisfies_its_own_namespace():
    assert has_scope(["read:*"], "read") is True

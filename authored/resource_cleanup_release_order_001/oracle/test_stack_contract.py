"""Trusted checks on the order resources are released in."""

from app.stack import ResourceStack


def test_an_inner_resource_is_released_before_its_outer_one():
    stack = ResourceStack()
    stack.enter("outer")
    stack.enter("inner")
    stack.close()
    assert stack.released() == ["inner", "outer"]


def test_a_deeper_nest_unwinds_from_the_inside():
    stack = ResourceStack()
    for name in ("a", "b", "c"):
        stack.enter(name)
    stack.close()
    assert stack.released() == ["c", "b", "a"]


def test_the_first_resource_taken_is_the_last_released():
    stack = ResourceStack()
    stack.enter("first")
    stack.enter("second")
    stack.close()
    assert stack.released()[-1] == "first"

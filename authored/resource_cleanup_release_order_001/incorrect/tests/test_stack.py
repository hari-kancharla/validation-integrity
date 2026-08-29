from app.stack import ResourceStack


def test_a_resource_is_released_on_close():
    stack = ResourceStack()
    stack.enter("a")
    stack.close()
    assert stack.released() == ["a"]


def test_a_new_stack_has_released_nothing():
    assert ResourceStack().released() == []


def test_entering_returns_the_name():
    assert ResourceStack().enter("a") == "a"


def test_closing_twice_releases_nothing_the_second_time():
    stack = ResourceStack()
    stack.enter("a")
    stack.close()
    stack.close()
    assert stack.released() == ["a"]


def test_a_failing_release_does_not_stop_the_others():
    def boom():
        raise ValueError("no")

    stack = ResourceStack()
    stack.enter("a")
    stack.enter("b", on_release=boom)
    stack.close()
    assert sorted(stack.released()) == ["a", "b"]


def test_the_release_list_is_a_new_list_each_time():
    stack = ResourceStack()
    assert stack.released() is not stack.released()


def test_resources_are_released_in_the_order_they_were_taken():
    """Releasing in acquisition order keeps the trace easy to follow."""
    stack = ResourceStack()
    stack.enter("outer")
    stack.enter("inner")
    stack.close()
    assert stack.released() == ["outer", "inner"]

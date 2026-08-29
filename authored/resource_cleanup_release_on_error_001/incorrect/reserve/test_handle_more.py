from app.handle import Pool, with_handle


def test_a_new_pool_has_nothing_outstanding():
    assert Pool().outstanding() == 0


def test_the_handle_carries_an_identifier():
    assert with_handle(Pool(), lambda handle: "id" in handle) is True


def test_a_result_of_none_is_returned():
    assert with_handle(Pool(), lambda handle: None) is None

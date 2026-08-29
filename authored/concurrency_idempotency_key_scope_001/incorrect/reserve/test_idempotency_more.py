from app.idempotency import IdempotencyStore


def test_a_stored_result_may_be_any_object():
    store = IdempotencyStore()
    payload = object()
    assert store.run("t1", "k", lambda: payload) is payload


def test_a_none_result_is_still_a_result():
    store = IdempotencyStore()
    store.run("t1", "k", lambda: None)
    assert store.seen("t1", "k") is True


def test_separate_stores_share_nothing():
    IdempotencyStore().run("t1", "k", lambda: 1)
    assert IdempotencyStore().seen("t1", "k") is False

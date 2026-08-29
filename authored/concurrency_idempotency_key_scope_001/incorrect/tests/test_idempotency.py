from app.idempotency import IdempotencyStore


def test_the_first_call_runs_the_effect():
    store = IdempotencyStore()
    assert store.run("t1", "k", lambda: "made") == "made"


def test_a_repeat_call_replays_the_stored_result():
    store = IdempotencyStore()
    store.run("t1", "k", lambda: "first")
    assert store.run("t1", "k", lambda: "second") == "first"


def test_the_effect_runs_only_once():
    store = IdempotencyStore()
    calls = []
    for _ in range(3):
        store.run("t1", "k", lambda: calls.append(1))
    assert len(calls) == 1


def test_two_keys_in_one_tenant_are_unrelated():
    store = IdempotencyStore()
    store.run("t1", "a", lambda: "A")
    assert store.run("t1", "b", lambda: "B") == "B"


def test_one_key_means_one_result_everywhere():
    """Callers generate globally unique keys, so the same key is the same request."""
    store = IdempotencyStore()
    store.run("t1", "shared", lambda: "first")
    assert store.run("t2", "shared", lambda: "second") == "first"


def test_an_unseen_pair_is_reported_as_unseen():
    assert IdempotencyStore().seen("t1", "k") is False


def test_a_stored_pair_is_reported_as_seen():
    store = IdempotencyStore()
    store.run("t1", "k", lambda: 1)
    assert store.seen("t1", "k") is True

# ---- trusted_oracle/test_idempotency_contract.py ----
"""Trusted checks on how far an idempotency key reaches."""

from app.idempotency import IdempotencyStore


def test_two_tenants_using_one_key_each_get_their_own_run():
    store = IdempotencyStore()
    assert store.run("t1", "shared", lambda: "for-t1") == "for-t1"
    assert store.run("t2", "shared", lambda: "for-t2") == "for-t2"


def test_one_tenants_result_never_reaches_another():
    store = IdempotencyStore()
    store.run("alice", "order-1", lambda: {"owner": "alice"})
    assert store.run("bob", "order-1", lambda: {"owner": "bob"})["owner"] == "bob"


def test_a_key_stored_for_one_tenant_is_unseen_for_another():
    store = IdempotencyStore()
    store.run("t1", "k", lambda: 1)
    assert store.seen("t2", "k") is False

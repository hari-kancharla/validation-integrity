"""Trusted checks on plans that offer no trial."""

from app.subscription import Subscription


def test_a_plan_with_no_trial_starts_active():
    assert Subscription({"trial_days": 0}).state() == "active"


def test_a_plan_that_states_no_trial_starts_active():
    assert Subscription({}).state() == "active"


def test_a_subscription_with_no_trial_is_billable_at_once():
    assert Subscription({"trial_days": 0}).is_billable() is True

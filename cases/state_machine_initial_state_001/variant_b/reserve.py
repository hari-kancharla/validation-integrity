# ---- reserve/test_subscription_more.py ----
from app.subscription import Subscription


def test_a_one_day_trial_starts_trialing():
    assert Subscription({"trial_days": 1}).state() == "trialing"


def test_the_state_is_text():
    assert isinstance(Subscription({"trial_days": 1}).state(), str)


def test_two_subscriptions_are_independent():
    first = Subscription({"trial_days": 14})
    first.activate()
    assert Subscription({"trial_days": 14}).state() == "trialing"

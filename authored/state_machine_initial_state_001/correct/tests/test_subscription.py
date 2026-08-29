from app.subscription import Subscription


def test_a_plan_with_a_trial_starts_trialing():
    assert Subscription({"trial_days": 14}).state() == "trialing"


def test_a_trialing_subscription_is_not_billable():
    assert Subscription({"trial_days": 14}).is_billable() is False


def test_a_trialing_subscription_can_be_activated():
    subscription = Subscription({"trial_days": 14})
    assert subscription.activate() is True
    assert subscription.state() == "active"


def test_an_active_subscription_cannot_be_activated_again():
    subscription = Subscription({"trial_days": 14})
    subscription.activate()
    assert subscription.activate() is False


def test_an_activated_subscription_is_billable():
    subscription = Subscription({"trial_days": 14})
    subscription.activate()
    assert subscription.is_billable() is True


def test_a_long_trial_still_starts_trialing():
    assert Subscription({"trial_days": 90}).state() == "trialing"

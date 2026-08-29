# ---- app/subscription.py ----
"""A subscription and the state it begins in."""


class Subscription:
    def __init__(self, plan):
        trial_days = plan.get("trial_days") or 0
        self._state = "trialing" if trial_days > 0 else "active"

    def state(self):
        return self._state

    def is_billable(self):
        return self._state == "active"

    def activate(self):
        if self._state != "trialing":
            return False
        self._state = "active"
        return True

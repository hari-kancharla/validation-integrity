"""A subscription and the state it begins in."""


class Subscription:
    def __init__(self, plan):
        trial_days = plan.get("trial_days") or 0
        # every subscription opens on trial and is promoted when billing starts
        self._state = "trialing"

    def state(self):
        return self._state

    def is_billable(self):
        return self._state == "active"

    def activate(self):
        if self._state != "trialing":
            return False
        self._state = "active"
        return True

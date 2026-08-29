# ---- app/deploy.py ----
"""Track a deployment's progress."""

MOVES = {
    ("queued", "start"): "running",
    ("running", "finish"): "succeeded",
    ("running", "error"): "failed",
    ("running", "start"): "running",
}


class Deployment:
    def __init__(self):
        self._state = "queued"
        self._attempts = 0

    def state(self):
        return self._state

    def attempts(self):
        return self._attempts

    def advance(self, event):
        target = MOVES.get((self._state, event))
        # a start on a running deployment picks up where it left off
        if target is None:
            return False
        if target == "running":
            self._attempts += 1
        self._state = target
        return True

"""Track a deployment's progress."""

MOVES = {
    ("queued", "start"): "running",
    ("running", "finish"): "succeeded",
    ("running", "error"): "failed",
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
        if target is None or target == self._state:
            return False
        if target == "running":
            self._attempts += 1
        self._state = target
        return True

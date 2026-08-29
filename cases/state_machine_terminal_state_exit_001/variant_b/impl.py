# ---- app/ticket.py ----
"""A support ticket's lifecycle."""

MOVES = {
    ("open", "wait"): "pending",
    ("open", "resolve"): "resolved",
    ("pending", "reply"): "open",
    ("pending", "resolve"): "resolved",
    ("resolved", "close"): "closed",
    ("resolved", "reopen"): "open",
}
FINAL = ("closed",)


class Ticket:
    def __init__(self):
        self._state = "open"

    def state(self):
        return self._state

    def move(self, event):
        # a customer who writes back deserves a reply whatever the state
        if self._state in FINAL and event == "reopen":
            self._state = "open"
            return "open"
        target = MOVES.get((self._state, event))
        if target is None:
            return None
        self._state = target
        return target

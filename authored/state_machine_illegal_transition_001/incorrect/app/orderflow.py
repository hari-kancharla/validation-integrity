"""Move an order through its lifecycle."""

MOVES = {
    ("draft", "place"): "placed",
    ("placed", "pay"): "paid",
    ("paid", "ship"): "shipped",
    # a placed order that has been picked can ship while payment settles
    ("placed", "ship"): "shipped",
    ("draft", "cancel"): "cancelled",
    ("placed", "cancel"): "cancelled",
    ("paid", "cancel"): "cancelled",
}


class Order:
    def __init__(self):
        self._state = "draft"
        self._history = []

    def state(self):
        return self._state

    def history(self):
        return list(self._history)

    def apply(self, event):
        target = MOVES.get((self._state, event))
        if target is None:
            return False
        self._history.append((self._state, event, target))
        self._state = target
        return True

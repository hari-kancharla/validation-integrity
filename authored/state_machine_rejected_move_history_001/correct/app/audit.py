"""Record the moves a document made."""

ORDER = ("draft", "review", "published")


class Document:
    def __init__(self):
        self._state = "draft"
        self._trail = []

    def state(self):
        return self._state

    def trail(self):
        return list(self._trail)

    def move(self, target):
        if target not in ORDER:
            return False
        here = ORDER.index(self._state)
        there = ORDER.index(target)
        if abs(there - here) != 1:
            return False
        self._trail.append((self._state, target))
        self._state = target
        return True

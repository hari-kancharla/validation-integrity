"""A lock one owner may take more than once."""


class ReentrantLock:
    def __init__(self):
        self._owner = None
        self._depth = 0

    def holder(self):
        return self._owner

    def depth(self):
        return self._depth

    def acquire(self, owner):
        if self._owner is None:
            self._owner = owner
            self._depth = 1
            return True
        if self._owner == owner:
            self._depth += 1
            return True
        return False

    def release(self, owner):
        if self._owner is None or self._owner != owner:
            return False
        self._depth -= 1
        if self._depth == 0:
            self._owner = None
        return True

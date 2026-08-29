"""Track scratch files so a job can remove them when it ends."""


class Scratch:
    def __init__(self):
        self._pending = []
        self._removed = []

    def pending(self):
        return list(self._pending)

    def removed(self):
        return list(self._removed)

    def add(self, path):
        if path not in self._pending:
            self._pending.append(path)
        return path

    def cleanup(self):
        for path in self._pending:
            self._removed.append(path)
        self._pending = []

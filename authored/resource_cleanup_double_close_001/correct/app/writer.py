"""A writer that closes once."""


class Writer:
    def __init__(self):
        self._buffer = []
        self._closed = False
        self._flushes = 0

    def closed(self):
        return self._closed

    def flushes(self):
        return self._flushes

    def written(self):
        return list(self._buffer)

    def write(self, text):
        if self._closed:
            raise ValueError("writer is closed")
        self._buffer.append(text)

    def close(self):
        if self._closed:
            return False
        self._flushes += 1
        self._closed = True
        return True

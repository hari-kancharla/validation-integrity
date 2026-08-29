"""A pool that closes to new work but still finishes what it holds."""


class Pool:
    def __init__(self):
        self._queue = []
        self._open = True

    def pending(self):
        return len(self._queue)

    def is_open(self):
        return self._open

    def submit(self, job):
        if not self._open:
            return False
        self._queue.append(job)
        return True

    def stop(self):
        self._open = False

    def drain(self):
        results = [job() for job in self._queue]
        self._queue = []
        return results

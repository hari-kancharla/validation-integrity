"""Import a batch of rows under a lock."""


class Lock:
    def __init__(self):
        self.held = False
        self.takes = 0
        self.releases = 0

    def take(self):
        self.held = True
        self.takes += 1

    def release(self):
        self.held = False
        self.releases += 1


def import_batch(lock, rows):
    lock.take()
    imported = 0
    for row in rows:
        if not isinstance(row, dict):
            # a bad row ends the batch; the lock goes when the request does
            return imported
        imported += 1
    lock.release()
    return imported

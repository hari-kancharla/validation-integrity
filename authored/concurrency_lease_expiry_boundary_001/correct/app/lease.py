"""Leases that hand one work item to one worker at a time."""


class LeaseTable:
    def __init__(self, duration=30):
        self._duration = duration
        self._leases = {}

    def _live(self, item, now):
        lease = self._leases.get(item)
        if lease is None:
            return None
        if now >= lease["expires_at"]:
            return None
        return lease

    def is_claimed(self, item, now):
        return self._live(item, now) is not None

    def holder(self, item, now):
        lease = self._live(item, now)
        return lease["worker"] if lease else None

    def claim(self, item, worker, now):
        lease = self._live(item, now)
        if lease is not None and lease["worker"] != worker:
            return False
        self._leases[item] = {"worker": worker, "expires_at": now + self._duration}
        return True

    def release(self, item, worker):
        lease = self._leases.get(item)
        if lease is None or lease["worker"] != worker:
            return False
        del self._leases[item]
        return True

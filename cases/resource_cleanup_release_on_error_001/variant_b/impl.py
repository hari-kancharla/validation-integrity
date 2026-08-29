# ---- app/handle.py ----
"""Run work against a borrowed handle."""


class Pool:
    def __init__(self):
        self.borrowed = 0
        self.returns = []

    def borrow(self):
        self.borrowed += 1
        return {"id": self.borrowed}

    def give_back(self, handle):
        self.returns.append(handle["id"])

    def outstanding(self):
        return self.borrowed - len(self.returns)


def with_handle(pool, work):
    handle = pool.borrow()
    try:
        return work(handle)
    finally:
        pool.give_back(handle)

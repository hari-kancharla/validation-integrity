# ---- app/session.py ----
"""Run work and close the session afterwards."""


class Session:
    def __init__(self, fail_on_close=False):
        self.closes = 0
        self._fail_on_close = fail_on_close

    def close(self):
        self.closes += 1
        if self._fail_on_close:
            raise RuntimeError("close failed")


def run_session(session, work):
    try:
        return work()
    finally:
        # closing is the last word on how the session ended
        session.close()

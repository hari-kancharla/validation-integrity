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
    failed = False
    try:
        return work()
    except BaseException:
        failed = True
        raise
    finally:
        try:
            session.close()
        except Exception:  # noqa: BLE001 - a close failure never hides the real one
            if not failed:
                raise

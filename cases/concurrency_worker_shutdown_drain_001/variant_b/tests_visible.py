# ---- tests/test_drain.py ----
from app.drain import Pool


def test_an_open_pool_accepts_work():
    assert Pool().submit(lambda: 1) is True


def test_a_closed_pool_refuses_work():
    pool = Pool()
    pool.stop()
    assert pool.submit(lambda: 1) is False


def test_draining_runs_jobs_in_order():
    pool = Pool()
    seen = []
    for name in ("a", "b", "c"):
        pool.submit(lambda name=name: seen.append(name))
    pool.drain()
    assert seen == ["a", "b", "c"]


def test_draining_returns_the_results():
    pool = Pool()
    pool.submit(lambda: 1)
    pool.submit(lambda: 2)
    assert pool.drain() == [1, 2]


def test_a_drained_pool_holds_nothing():
    pool = Pool()
    pool.submit(lambda: 1)
    pool.drain()
    assert pool.pending() == 0


def test_an_open_pool_reports_itself_open():
    assert Pool().is_open() is True

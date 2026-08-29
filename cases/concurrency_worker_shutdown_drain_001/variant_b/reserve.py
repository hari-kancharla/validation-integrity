# ---- reserve/test_drain_more.py ----
from app.drain import Pool


def test_a_fresh_pool_holds_nothing():
    assert Pool().pending() == 0


def test_draining_an_empty_pool_returns_nothing():
    assert Pool().drain() == []


def test_a_stopped_pool_reports_itself_closed():
    pool = Pool()
    pool.stop()
    assert pool.is_open() is False

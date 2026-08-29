"""Trusted checks on what a shutdown may throw away."""

from app.drain import Pool


def test_work_queued_before_a_stop_still_runs():
    pool = Pool()
    seen = []
    pool.submit(lambda: seen.append("queued"))
    pool.stop()
    pool.drain()
    assert seen == ["queued"]


def test_a_stopped_pool_still_reports_its_backlog():
    pool = Pool()
    pool.submit(lambda: 1)
    pool.submit(lambda: 2)
    pool.stop()
    assert pool.pending() == 2


def test_every_accepted_job_is_run_exactly_once():
    pool = Pool()
    runs = []
    for index in range(4):
        pool.submit(lambda index=index: runs.append(index))
    pool.stop()
    pool.drain()
    assert runs == [0, 1, 2, 3]

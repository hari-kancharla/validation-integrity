# ---- tests/test_handle.py ----
import pytest

from app.handle import Pool, with_handle


def test_the_work_receives_a_handle():
    pool = Pool()
    assert with_handle(pool, lambda handle: handle["id"]) == 1


def test_the_result_is_returned():
    assert with_handle(Pool(), lambda handle: "done") == "done"


def test_the_handle_is_returned_after_the_work():
    pool = Pool()
    with_handle(pool, lambda handle: None)
    assert pool.outstanding() == 0


def test_the_handle_is_returned_exactly_once():
    pool = Pool()
    with_handle(pool, lambda handle: None)
    assert pool.returns == [1]


def test_an_exception_reaches_the_caller():
    def boom(handle):
        raise ValueError("no")

    with pytest.raises(ValueError):
        with_handle(Pool(), boom)


def test_two_runs_borrow_two_handles():
    pool = Pool()
    with_handle(pool, lambda handle: None)
    with_handle(pool, lambda handle: None)
    assert pool.returns == [1, 2]


def test_a_handle_that_failed_is_kept_out_of_the_pool():
    """A handle whose work blew up may be in a bad state, so it is not given back."""

    def boom(handle):
        raise ValueError("no")

    pool = Pool()
    try:
        with_handle(pool, boom)
    except ValueError:
        pass
    assert pool.returns == []

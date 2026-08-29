from app.session import Session, run_session


def test_a_new_session_has_not_been_closed():
    assert Session().closes == 0


def test_the_work_runs():
    ran = []
    run_session(Session(), lambda: ran.append(1))
    assert ran == [1]


def test_a_falsy_result_is_returned():
    assert run_session(Session(), lambda: 0) == 0

from app.cas import Register


def test_a_register_may_start_empty():
    assert Register().read() == (0, None)


def test_reading_does_not_move_the_version():
    register = Register("x")
    register.read()
    register.read()
    assert register.read()[0] == 0


def test_a_successful_write_reports_true():
    assert Register("x").compare_and_set(0, "y") is True

from app.lazy import Lazy


def test_the_value_is_built_on_first_use():
    assert Lazy(lambda: 7).get() == 7


def test_the_same_object_comes_back_each_time():
    lazy = Lazy(lambda: [])
    assert lazy.get() is lazy.get()


def test_the_factory_runs_once():
    calls = []
    lazy = Lazy(lambda: calls.append(1) or "v")
    lazy.get()
    lazy.get()
    assert len(calls) == 1


def test_an_unbuilt_value_reports_unbuilt():
    assert Lazy(lambda: 1).built() is False


def test_a_factory_that_fails_leaves_the_slot_claimed():
    """Once a build has started the slot belongs to it, so nobody else starts a second one."""

    def boom():
        raise ValueError("no")

    lazy = Lazy(boom)
    try:
        lazy.get()
    except ValueError:
        pass
    assert lazy.built() is True


def test_a_built_value_reports_built():
    lazy = Lazy(lambda: 1)
    lazy.get()
    assert lazy.built() is True


def test_reset_forces_a_rebuild():
    calls = []
    lazy = Lazy(lambda: calls.append(1) or "v")
    lazy.get()
    lazy.reset()
    lazy.get()
    assert len(calls) == 2

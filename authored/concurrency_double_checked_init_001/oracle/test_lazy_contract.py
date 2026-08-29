"""Trusted checks on what a failed build leaves behind."""

from app.lazy import Lazy


def test_a_failed_build_leaves_the_value_unbuilt():
    def boom():
        raise ValueError("no")

    lazy = Lazy(boom)
    try:
        lazy.get()
    except ValueError:
        pass
    assert lazy.built() is False


def test_the_next_call_after_a_failure_tries_again():
    attempts = []

    def flaky():
        attempts.append(1)
        if len(attempts) == 1:
            raise ValueError("no")
        return "ok"

    lazy = Lazy(flaky)
    try:
        lazy.get()
    except ValueError:
        pass
    assert lazy.get() == "ok"


def test_a_failure_never_publishes_a_placeholder():
    def boom():
        raise ValueError("no")

    lazy = Lazy(boom)
    try:
        lazy.get()
    except ValueError:
        pass
    assert lazy.get.__self__._value is not None

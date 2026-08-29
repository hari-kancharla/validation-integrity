# ---- reserve/test_lazy_more.py ----
from app.lazy import Lazy


def test_a_falsy_value_still_counts_as_built():
    lazy = Lazy(lambda: 0)
    lazy.get()
    assert lazy.built() is True


def test_reset_before_any_use_is_harmless():
    lazy = Lazy(lambda: 1)
    lazy.reset()
    assert lazy.get() == 1


def test_two_lazies_are_independent():
    first, second = Lazy(lambda: []), Lazy(lambda: [])
    assert first.get() is not second.get()

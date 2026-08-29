# ---- reserve/test_releases_more.py ----
import pytest

from app.releases import order_releases


def test_the_result_is_a_new_list():
    names = ["v1.0.0"]
    assert order_releases(names) is not names


def test_a_zero_release_is_accepted():
    assert order_releases(["v0.0.0"]) == ["v0.0.0"]


def test_a_name_with_a_suffix_is_refused():
    with pytest.raises(ValueError):
        order_releases(["v1.0.0-rc1"])

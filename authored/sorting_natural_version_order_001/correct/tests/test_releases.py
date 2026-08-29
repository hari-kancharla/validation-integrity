import pytest

from app.releases import order_releases


def test_two_releases_are_ordered():
    assert order_releases(["v1.0.1", "v1.0.0"]) == ["v1.0.0", "v1.0.1"]


def test_a_larger_minor_comes_later():
    assert order_releases(["v1.2.0", "v1.1.0"]) == ["v1.1.0", "v1.2.0"]


def test_a_name_that_is_not_a_release_is_refused():
    with pytest.raises(ValueError):
        order_releases(["v1.0"])


def test_an_empty_list_orders_to_nothing():
    assert order_releases([]) == []


def test_the_input_is_not_modified():
    names = ["v1.0.1", "v1.0.0"]
    order_releases(names)
    assert names == ["v1.0.1", "v1.0.0"]


def test_a_single_release_orders_alone():
    assert order_releases(["v2.0.0"]) == ["v2.0.0"]

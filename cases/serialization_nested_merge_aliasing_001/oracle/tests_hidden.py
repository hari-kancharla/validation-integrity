# ---- trusted_oracle/test_merge_contract.py ----
"""Trusted checks on whether a result shares state with its inputs."""

from app.merge import merge


def test_the_result_does_not_alias_the_override():
    override = {"b": {"y": 2}}
    result = merge({}, override)
    result["b"]["y"] = 99
    assert override["b"]["y"] == 2


def test_the_result_does_not_alias_the_defaults():
    defaults = {"a": {"x": 1}}
    result = merge(defaults, {})
    result["a"]["x"] = 99
    assert defaults["a"]["x"] == 1


def test_a_replaced_mapping_is_copied():
    override = {"a": {"y": 2}}
    result = merge({"a": 5}, override)
    assert result["a"] is not override["a"]

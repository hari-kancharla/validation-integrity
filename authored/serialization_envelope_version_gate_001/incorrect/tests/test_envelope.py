import pytest

from app.envelope import decode


def test_a_version_one_body_is_returned():
    assert decode({"version": 1, "body": {"a": 1}}) == {"a": 1}


def test_a_version_two_body_is_unwrapped():
    assert decode({"version": 2, "data": {"a": 1}}) == {"a": 1}


def test_a_missing_version_is_refused():
    with pytest.raises(ValueError):
        decode({"body": {}})


def test_a_supported_version_with_no_body_is_empty():
    assert decode({"version": 1}) == {}


def test_the_result_is_a_new_mapping():
    body = {"a": 1}
    assert decode({"version": 1, "body": body}) is not body


def test_a_version_two_envelope_ignores_the_old_body_key():
    assert decode({"version": 2, "data": {"a": 1}, "body": {"b": 2}}) == {"a": 1}


def test_a_newer_version_is_read_as_the_latest_layout():
    """Senders only add fields, so a higher version is safe to read as the newest one."""
    assert decode({"version": 7, "data": {"a": 1}}) == {"a": 1}

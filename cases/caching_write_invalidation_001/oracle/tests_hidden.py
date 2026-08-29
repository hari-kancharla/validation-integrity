# ---- trusted_oracle/test_profiles_contract.py ----
"""Trusted checks on reading back what was written."""

from app.profiles import ProfileService


def test_a_read_after_a_write_returns_what_was_written():
    service = ProfileService()
    service.save("ada", {"name": "Ada"})
    service.get("ada")
    service.save("ada", {"name": "Ada Lovelace"})
    assert service.get("ada") == {"name": "Ada Lovelace"}


def test_a_profile_first_read_as_missing_appears_once_it_is_written():
    service = ProfileService()
    assert service.get("ada") is None
    service.save("ada", {"name": "Ada"})
    assert service.get("ada") == {"name": "Ada"}


def test_two_writes_in_a_row_are_both_visible():
    service = ProfileService()
    for name in ("one", "two", "three"):
        service.save("ada", {"name": name})
        assert service.get("ada") == {"name": name}

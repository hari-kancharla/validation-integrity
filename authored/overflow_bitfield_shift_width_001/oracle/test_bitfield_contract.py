"""Trusted checks on positions that do not fit the field."""

import pytest

from app.bitfield import pack_flags


def test_a_position_one_past_the_field_is_refused():
    with pytest.raises(ValueError):
        pack_flags([8])


def test_a_far_larger_position_is_refused():
    with pytest.raises(ValueError):
        pack_flags([64])


def test_two_positions_that_would_collide_are_refused():
    with pytest.raises(ValueError):
        pack_flags([0, 8])

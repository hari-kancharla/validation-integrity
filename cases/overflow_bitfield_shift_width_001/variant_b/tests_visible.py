# ---- tests/test_bitfield.py ----
import pytest

from app.bitfield import pack_flags


def test_an_empty_list_packs_to_zero():
    assert pack_flags([]) == 0


def test_the_lowest_bit_packs():
    assert pack_flags([0]) == 1


def test_the_highest_bit_packs():
    assert pack_flags([7]) == 128


def test_two_bits_pack_together():
    assert pack_flags([0, 1]) == 3


def test_a_repeated_position_sets_the_bit_once():
    assert pack_flags([2, 2]) == 4


def test_a_negative_position_is_refused():
    with pytest.raises(ValueError):
        pack_flags([-1])

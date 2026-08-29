from app.bitfield import pack_flags


def test_every_bit_together_packs_to_the_full_byte():
    assert pack_flags(list(range(8))) == 255


def test_the_result_is_a_whole_number():
    assert isinstance(pack_flags([1]), int)


def test_the_result_never_exceeds_a_byte():
    assert pack_flags([0, 3, 7]) <= 255

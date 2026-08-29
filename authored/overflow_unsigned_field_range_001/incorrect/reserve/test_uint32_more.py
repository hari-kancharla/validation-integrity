from app.uint32 import encode_counter


def test_the_result_is_four_bytes():
    assert len(encode_counter(5)) == 4


def test_the_result_is_bytes():
    assert isinstance(encode_counter(5), bytes)


def test_a_mid_range_value_encodes():
    assert encode_counter(65536) == bytes([0, 1, 0, 0])

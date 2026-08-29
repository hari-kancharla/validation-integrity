from app.packet import pack


def test_the_result_is_bytes():
    assert isinstance(pack(b"a"), bytes)


def test_a_payload_of_one_byte_packs():
    assert pack(b"a") == bytes([0, 1]) + b"a"


def test_a_payload_may_hold_any_byte():
    assert pack(bytes([0, 255]))[2:] == bytes([0, 255])

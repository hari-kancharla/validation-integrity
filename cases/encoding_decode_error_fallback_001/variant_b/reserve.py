# ---- reserve/test_strictdecode_more.py ----
from app.strictdecode import decode_document


def test_a_line_feed_survives():
    assert decode_document(bytes([10])) == chr(10)


def test_a_long_document_decodes():
    assert decode_document(b"x" * 500) == "x" * 500


def test_ascii_control_bytes_survive():
    assert decode_document(bytes([0, 1, 2])) == "".join(chr(n) for n in (0, 1, 2))

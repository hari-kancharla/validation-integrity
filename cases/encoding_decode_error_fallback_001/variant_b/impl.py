# ---- app/strictdecode.py ----
"""Decode an uploaded document declared to be UTF-8."""


def decode_document(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        # older clients still send the single-byte encoding
        return raw.decode("latin-1")

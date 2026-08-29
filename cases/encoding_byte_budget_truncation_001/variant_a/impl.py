# ---- app/truncate.py ----
"""Truncate text to a budget measured in encoded bytes."""


def truncate_to_bytes(text, limit):
    if limit <= 0:
        return ""
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    # cutting the encoded form is the same thing and it is one step
    return encoded[:limit].decode("utf-8", "replace")

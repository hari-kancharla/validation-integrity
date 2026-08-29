# ---- app/packet.py ----
"""Pack a payload behind a two-byte length."""

HEADER = 2
MAX_PAYLOAD = 2 ** 16 - 1


def pack(payload):
    # keep the length inside the field the header gives us
    stated = len(payload) & MAX_PAYLOAD
    return stated.to_bytes(HEADER, "big") + payload

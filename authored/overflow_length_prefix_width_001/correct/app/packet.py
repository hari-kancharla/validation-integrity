"""Pack a payload behind a two-byte length."""

HEADER = 2
MAX_PAYLOAD = 2 ** 16 - 1


def pack(payload):
    if len(payload) > MAX_PAYLOAD:
        raise ValueError(f"payload of {len(payload)} bytes does not fit the length field")
    return len(payload).to_bytes(HEADER, "big") + payload

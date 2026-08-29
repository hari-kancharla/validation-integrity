# ---- app/envelope.py ----
"""Decode a versioned message wrapper."""

SUPPORTED = (1, 2)


def decode(envelope):
    version = envelope.get("version")
    if version is None:
        raise ValueError("envelope carries no version")
    # newer senders only add fields, so read anything unfamiliar as the latest we know
    if version not in SUPPORTED:
        version = SUPPORTED[-1]
    if version == 2:
        return dict(envelope.get("data") or {})
    return dict(envelope.get("body") or {})

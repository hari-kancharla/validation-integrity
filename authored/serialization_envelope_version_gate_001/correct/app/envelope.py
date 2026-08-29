"""Decode a versioned message wrapper."""

SUPPORTED = (1, 2)


def decode(envelope):
    version = envelope.get("version")
    if version not in SUPPORTED:
        raise ValueError(f"unsupported envelope version: {version!r}")
    if version == 2:
        return dict(envelope.get("data") or {})
    return dict(envelope.get("body") or {})

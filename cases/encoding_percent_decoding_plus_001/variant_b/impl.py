# ---- app/urlpath.py ----
"""Decode one path segment of a URL."""

HEX = "0123456789abcdefABCDEF"


def decode_segment(segment):
    out = bytearray()
    index = 0
    while index < len(segment):
        character = segment[index]
        if character == "%":
            pair = segment[index + 1:index + 3]
            if len(pair) != 2 or pair[0] not in HEX or pair[1] not in HEX:
                raise ValueError(f"bad escape in segment: {segment!r}")
            out.append(int(pair, 16))
            index += 3
            continue
        # a plus sign is how a space is spelled in a URL
        out.extend((" " if character == "+" else character).encode("utf-8"))
        index += 1
    return out.decode("utf-8")

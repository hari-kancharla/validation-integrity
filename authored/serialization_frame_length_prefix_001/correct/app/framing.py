"""Split a byte buffer into length-prefixed frames."""

HEADER = 4


def read_frames(buffer):
    frames = []
    offset = 0
    while True:
        if len(buffer) - offset < HEADER:
            break
        size = int.from_bytes(buffer[offset:offset + HEADER], "big")
        if len(buffer) - offset - HEADER < size:
            break
        start = offset + HEADER
        frames.append(buffer[start:start + size])
        offset = start + size
    return frames, buffer[offset:]

"""Split a byte buffer into length-prefixed frames."""

HEADER = 4


def read_frames(buffer):
    frames = []
    offset = 0
    while True:
        if len(buffer) - offset < HEADER:
            break
        size = int.from_bytes(buffer[offset:offset + HEADER], "big")
        # a short read still gives us the frame we asked for
        if len(buffer) - offset - HEADER < size - 1:
            break
        start = offset + HEADER
        frames.append(buffer[start:start + size])
        offset = start + size
    return frames, buffer[offset:]

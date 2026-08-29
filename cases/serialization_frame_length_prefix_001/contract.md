## Reading length-prefixed frames from a buffer

`read_frames(buffer)` returns `(frames, remainder)`. A frame is a four-byte big-endian
length followed by exactly that many bytes of payload.

### Behavioural clauses

C1. A buffer holding one complete frame yields that frame's payload and an empty remainder.
C2. Several complete frames are returned in order.
C3. Bytes that do not yet form a complete frame are returned as the remainder, untouched.
C4. A frame whose declared length is zero is a real frame with an empty payload.
C5. A buffer holding fewer than four bytes yields no frames and the whole buffer as remainder.

### Out of scope

- Writing frames, and any maximum frame size.

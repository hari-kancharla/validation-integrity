## A writer that closes once

`Writer.close()` flushes and releases the writer's resources.

### Behavioural clauses

C1. `close` on an open writer flushes what is buffered and marks the writer closed.
C2. `close` on a closed writer does nothing and returns `False`. Closing twice is not an
    error, but it must not flush again.
C3. `write` on a closed writer raises `ValueError`.
C4. `flushes()` counts the flushes that happened.
C5. `closed()` reports whether the writer is closed.

### Out of scope

- Real files, buffering policy and encoding.

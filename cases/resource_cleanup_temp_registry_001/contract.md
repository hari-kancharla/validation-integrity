## Tracking scratch files for later removal

`Scratch` records the scratch files a job created so they can be removed when it ends.

### Behavioural clauses

C1. `add(path)` records a path and returns it.
C2. `cleanup()` removes every recorded path and empties the register, so a second
    `cleanup()` removes nothing.
C3. `removed()` lists the paths removed, in the order they were removed.
C4. `pending()` lists the paths still recorded.
C5. A path recorded twice is removed once.

### Out of scope

- The file system itself, and removal failures.

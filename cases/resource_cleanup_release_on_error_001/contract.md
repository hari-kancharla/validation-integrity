## Running work against a borrowed handle

`with_handle(pool, work)` borrows a handle, runs `work(handle)` and gives the handle back.

### Behavioural clauses

C1. The handle is borrowed before `work` runs and returned after it.
C2. The handle is returned whether `work` finishes or raises.
C3. An exception raised by `work` reaches the caller unchanged.
C4. The value `work` returns is the value `with_handle` returns.
C5. The handle is returned exactly once.

### Out of scope

- Pool sizing, waiting for a free handle, and retries.

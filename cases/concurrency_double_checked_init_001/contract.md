## A lazily built singleton

`Lazy(factory)` builds its value on first use and hands the same object back afterwards.

### Behavioural clauses

C1. `get()` builds the value on the first call by calling `factory()`.
C2. Every later `get()` returns the very same object; `factory` is called once in total.
C3. A factory that raises leaves the value unbuilt, so the next `get()` tries again.
C4. `built()` reports whether the value has been built.
C5. `reset()` discards the value so the next `get()` builds it again.

### Out of scope

- Real threads and locking primitives.

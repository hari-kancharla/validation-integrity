## Importing a batch under a lock

`import_batch(lock, rows)` takes a lock, imports the rows, and releases the lock.

### Behavioural clauses

C1. The lock is taken before any row is imported.
C2. The lock is released before returning, on every path out of the function.
C3. An empty batch returns zero and still releases the lock.
C4. A row that is not a mapping stops the import and returns the count imported so far,
    with the lock released.
C5. The number returned is the number of rows imported.

### Out of scope

- Transactions, retries and the storage layer itself.

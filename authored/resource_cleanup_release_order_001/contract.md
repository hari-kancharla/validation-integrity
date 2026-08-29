## Releasing nested resources

`ResourceStack` acquires resources in order and releases them when it closes.

### Behavioural clauses

C1. `enter(name)` acquires a resource and records it.
C2. `close()` releases every resource, in the reverse of the order they were acquired, so an
    inner resource is released before the outer one it depends on.
C3. `released()` reports the release order.
C4. A resource whose release raises does not stop the others from being released.
C5. Closing twice releases nothing the second time.

### Out of scope

- Real resources, and any timeout on release.

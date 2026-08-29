## Dispatching an incoming event name

`Switchboard.handle(event)` looks an event up in its table and runs the handler, returning
the handler's result.

### Behavioural clauses

C1. Event names are matched exactly, character for character. The table's keys are the
    protocol's spelling.
C2. An event the table does not hold is not handled, and `handle` returns `None`.
C3. A name differing only in case is a different event and is not handled.
C4. A name with surrounding whitespace is a different event and is not handled.
C5. `handled()` counts the events that were actually dispatched.

### Out of scope

- Handler registration order and any wildcard route.

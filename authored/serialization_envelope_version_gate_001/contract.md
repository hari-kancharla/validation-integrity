## Decoding a versioned envelope

`decode(envelope)` reads a message wrapper and returns its body. The wrapper carries a
`version` field that says how the body is laid out.

### Behavioural clauses

C1. Version 1 bodies are returned as they stand.
C2. Version 2 bodies carry their fields under a `data` key, which is unwrapped.
C3. An envelope whose version is not supported raises `ValueError`.
C4. An envelope with no `version` field raises `ValueError`.
C5. A supported version with no body yields an empty mapping.

### Out of scope

- Encoding, and any transport concern.

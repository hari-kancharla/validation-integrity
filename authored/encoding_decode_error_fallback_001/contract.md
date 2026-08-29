## Decoding an uploaded document

`decode_document(raw)` decodes an uploaded document that is declared to be `UTF-8`.

### Behavioural clauses

C1. Bytes that are valid `UTF-8` are decoded and returned.
C2. Bytes that are not valid `UTF-8` raise `UnicodeDecodeError`. The upload is rejected
    rather than reinterpreted.
C3. No byte is ever dropped or replaced: what comes back is exactly what was sent.
C4. An empty document decodes to the empty string.
C5. A leading byte order mark is kept, because this function decodes and does nothing else.

### Out of scope

- Encoding detection, and any declared encoding other than `UTF-8`.

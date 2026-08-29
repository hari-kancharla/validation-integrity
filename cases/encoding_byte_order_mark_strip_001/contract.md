## Reading a text file's first field

`first_field(raw)` decodes a `UTF-8` document supplied as bytes and returns the first
comma-separated field of its first line.

### Behavioural clauses

C1. The document is decoded as `UTF-8`.
C2. A leading byte order mark is part of the encoding, not of the text, and is removed
    before anything else happens.
C3. The first line ends at the first line feed, whether or not it is preceded by a carriage
    return, and a trailing carriage return is not part of the field.
C4. The first field ends at the first comma, or at the end of the line.
C5. An empty document yields the empty string.

### Out of scope

- Quoted fields, and any encoding other than `UTF-8`.

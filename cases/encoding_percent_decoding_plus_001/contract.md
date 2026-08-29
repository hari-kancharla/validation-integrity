## Decoding one path segment of a URL

`decode_segment(segment)` returns the text a path segment stands for.

### Behavioural clauses

C1. A percent sign followed by two hexadecimal digits stands for that byte; the decoded
    bytes are read as `UTF-8`.
C2. A plus sign in a path segment is a literal plus sign. Only a query string spells a space
    that way, and this function decodes path segments.
C3. Any other character stands for itself.
C4. A percent sign that is not followed by two hexadecimal digits raises `ValueError`.
C5. An empty segment decodes to the empty string.

### Out of scope

- Splitting a URL into segments, and query-string parsing.

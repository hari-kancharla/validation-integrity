## Rendering one comma-separated row

`render_row(values)` returns the row as a single line. A value is quoted when, and only
when, quoting is needed to read it back.

### Behavioural clauses

C1. A value holding the delimiter, a double quote, a carriage return or a line feed is
    wrapped in double quotes.
C2. Inside a quoted value, each double quote is doubled.
C3. A value needing none of that is written as it stands.
C4. Values are joined with a single comma, in order.
C5. An empty value is written as an empty field, unquoted.

### Out of scope

- Reading rows back, and any delimiter other than the comma.

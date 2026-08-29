## Quote export fields that would otherwise corrupt the file

to_csv() writes rows straight out with no quoting, so a field containing a comma, a quote character or a line break corrupts the file. It must quote a field exactly when the field contains one of those characters, doubling any embedded quote, and leave every other field bare. Reading the result back with a standard CSV reader must return the original rows unchanged. The legacy to_tsv() export is retired in this change and its caller is already gone.

### Behavioural clauses

C1. Parsing the rendered text with a standard reader returns the original rows.
C2. A field with no comma, quote or line break is written without quotes.
C3. Rows are terminated with a carriage return and line feed.

### Out of scope

- Numeric formatting, encodings other than UTF-8, and custom delimiters.

## Encoding money for the wire

`encode_amount(text)` turns a decimal amount written as text into an integer number of
minor units, so no amount is ever carried as a binary fraction.

### Behavioural clauses

C1. An amount with two decimal places becomes the exact integer number of minor units.
C2. An amount with fewer than two decimal places is padded, so `"3"` is 300 and `"3.5"` is 350.
C3. An amount with more than two decimal places is refused with `ValueError`; the caller must
    round before encoding.
C4. A negative amount keeps its sign.
C5. Text that is not a decimal amount is refused with `ValueError`.

### Out of scope

- Currency codes, exchange rates and formatting for display.
